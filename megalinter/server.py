# !/usr/bin/env python3
"""
Start MegaLinter server
"""
import logging
from uuid import uuid1
from enum import StrEnum
import git
import tempfile

from pydantic import BaseModel
from megalinter import config, alpaca, MegaLinter
from fastapi import BackgroundTasks, FastAPI, Response, status, HTTPException
from fastapi.responses import JSONResponse

print("MegaLinter Server starting...")
logging.config.fileConfig("logging.conf", disable_existing_loggers=False)
logger = logging.getLogger(__name__)
alpaca()
app = FastAPI(title="MegaLinter Server", version=config.get("BUILD_VERSION", "DEV"))

global running_process_number, max_running_process_number, ANALYSIS_REQUESTS
running_process_number = 0
max_running_process_number = 1
ANALYSIS_REQUESTS = []


# Get status of MegaLinter server
@app.get("/", status_code=status.HTTP_200_OK)
async def read_root():
    global running_process_number, max_running_process_number
    return {
        "version": app.version,
        "runningProcessNumber": running_process_number,
        "maxRunningProcessNumber": max_running_process_number,
        "available": running_process_number < max_running_process_number,
    }


# Analysis request model
class AnalysisRequestItem(BaseModel):
    inputString: str | None = None
    repositoryUrl: str | None = None
    webHookUrl: str | None = None


# Get info about a request
@app.get("/analysis/{item_id}", status_code=status.HTTP_200_OK)
async def get_analysis(item_id):
    global ANALYSIS_REQUESTS
    analysis_request = AnalysisRequest.findById(item_id)
    if analysis_request is not None:
        return JSONResponse(content=analysis_request.toJsonObject())
    raise HTTPException(
        status_code=404, detail=f"Unable to find analysis request {item_id}"
    )

# Find request by repository url
@app.get("/analysis/", status_code=status.HTTP_200_OK)
async def get_analysis(repo: str):
    global ANALYSIS_REQUESTS
    analysis_request = AnalysisRequest.findByRepository(repo)
    if analysis_request is not None:
        return JSONResponse(content=analysis_request.toJsonObject())
    raise HTTPException(
        status_code=404, detail=f"Unable to find analysis request for repository {repo}"
    )

# Post a new request to MegaLinter
@app.post("/analysis", status_code=status.HTTP_102_PROCESSING)
async def request_analysis(
    background_tasks: BackgroundTasks,
    item: AnalysisRequestItem | None = None,
) -> Response:
    # Check server is available
    global running_process_number, max_running_process_number
    if running_process_number >= max_running_process_number:
        raise HTTPException(
            status_code=423, detail=f"The server is already processing the max number of requests ({max_running_process_number})"
        )
    # Increment number of processed requests
    running_process_number += 1
    analysis_request = AnalysisRequest()
    analysis_request.initialize(item)
    analysis_request.initialize_files()
    analysis_request.save()
    background_tasks.add_task(start_analysis, analysis_request.id)
    return JSONResponse(content=analysis_request.toJsonObject())


# Analysis status enum
class AnalysisStatus(StrEnum):
    NEW = "new"
    IN_PROGRESS = "in-progress"
    COMPLETE = "complete"


def start_analysis(analysis_request_id: str):
    analysis_request: AnalysisRequest = AnalysisRequest.findById(analysis_request_id)
    analysis_request.process()
    global running_process_number
    running_process_number -= 1


# Analysis processor class
class AnalysisRequest(BaseModel):
    id: str | None = None
    status: AnalysisStatus | None = None
    repository: str | None = None
    request_item: AnalysisRequestItem | None = None
    workspace: str | None = None
    web_hook_url : str | None = None

    # Find analysis request from unique id: Could be using external database in the future
    @staticmethod
    def findById(static_analysis_id: str):
        global ANALYSIS_REQUESTS
        for analysis_request in ANALYSIS_REQUESTS:
            if analysis_request.id == static_analysis_id:
                return analysis_request
        return None

    # Find analysis request from unique key, like a repository url
    @staticmethod
    def findByRepository(repository: str):
        global ANALYSIS_REQUESTS
        for analysis_request in ANALYSIS_REQUESTS:
            if analysis_request.repository == repository:
                return analysis_request
        return None

    def initialize(self, request_item: AnalysisRequestItem):
        self.id = str(uuid1())
        self.status = AnalysisStatus.NEW
        self.request_item = request_item
        if request_item.webHookUrl:
            self.web_hook_url = request_item.webHookUrl
        logger.info(f"Analysis request {self.id} has been initialized")

    def initialize_files(self):
        # Clone repo from provided url
        if self.request_item.repositoryUrl:
            temp_dir = tempfile.mkdtemp()
            try:
                git.Repo.clone_from(self.request_item.repositoryUrl, temp_dir)
            except Exception as e:
                self.stop_request()
                raise HTTPException(
                    status_code=404, detail=f"Unable to clone repository\n{str(e)}"
                )
            logger.info(
                f"Cloned {self.request_item.repositoryUrl} in temp dir {temp_dir}"
            )
            self.workspace = temp_dir
            self.repository = self.request_item.repositoryUrl
            return
        # Nothing to create a request !
        self.stop_request()
        raise HTTPException(
            status_code=422,
            detail="Unable to initialize files for analysis",  # Unprocessable content
        )

    def toJsonObject(self):
        return {
            "id": self.id,
            "status": self.status,
            "requestItem": {
                "inputString": self.request_item.inputString,
                "repositoryUrl": self.request_item.repositoryUrl,
            },
        }

    def stop_request():
        global running_process_number
        running_process_number -= 1

    def change_status(self, status: AnalysisStatus):
        self.status = status
        logger.info(f"Analysis request {self.id} status change: {status}")
        self.save()

    # Save state of Analysis Request (Could be using external database in the future)
    def save(self):
        global ANALYSIS_REQUESTS
        existing_analysis_request = AnalysisRequest.findById(self.id)
        if existing_analysis_request is not None:
            for index, x in enumerate(ANALYSIS_REQUESTS):
                if x.id == self.id:
                    ANALYSIS_REQUESTS[index] = self
                    break
        else:
            ANALYSIS_REQUESTS.append(self)
        logger.info(f"Analysis request {self.id} has been saved")

    def process(self):
        mega_linter = MegaLinter.Megalinter({
            "request_id": self.id,
            "workspace": self.workspace,
            "SARIF_REPORTER": "true",
            "WEBHOOK_REPORTER": "true",
            "WEBHOOK_REPORTER_URL": self.web_hook_url
        })
        self.change_status(AnalysisStatus.IN_PROGRESS)
        mega_linter.run()
        self.change_status(AnalysisStatus.COMPLETE)
        del mega_linter
