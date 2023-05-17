# !/usr/bin/env python3
"""
Start MegaLinter server
"""
import logging
import os
import tempfile
import typing
from enum import StrEnum
from typing import List
from uuid import uuid1

import git
from fastapi import BackgroundTasks, FastAPI, HTTPException, Response, status
from megalinter import MegaLinter, alpaca, config
from pydantic import BaseModel, Field
from pygments import lexers

print("MegaLinter Server starting…")
logging.config.fileConfig("logging.conf", disable_existing_loggers=False)  # type: ignore[attr-defined]
logger = logging.getLogger(__name__)
alpaca()
app = FastAPI(
    title="MegaLinter Server", version=config.get(None, "BUILD_VERSION", "DEV")
)

global running_process_number, max_running_process_number, ANALYSIS_EXECUTIONS
running_process_number = 0
max_running_process_number = int(os.environ.get("MAX_RUNNING_PROCESS_NUMBER", 5))
total_process_number_run = 0
ANALYSIS_EXECUTIONS: List[typing.Any] = []

###############
####  API  #### # noqa: E266
###############


# Analysis status enum
class AnalysisStatus(StrEnum):
    NEW = "new"
    IN_PROGRESS = "in-progress"
    COMPLETE = "complete"


# Analysis request model
class AnalysisRequestInput(BaseModel):
    snippet: str | None = Field(
        default=None,
        description="Input any code snippet",
        example="#!/usr/bin/env python3",
    )
    repositoryUrl: str | None = Field(
        default=None,
        description="Input a public repository url",
        example="https://github.com/nvuillam/github-dependents-info",
    )
    webHookUrl: str | None = Field(
        default=None,
        description="WebHook URL to receive results",
        example="https://9faea506-7e84-4f5d-a68f-86bbdfgT5t.mock.pstmn.io/webhook",
    )

    class Config:
        schema_extra = {
            "example": {
                "repositoryUrl": "https://github.com/nvuillam/github-dependents-info",
                "webHookUrl": "https://9faea506-7e84-4f5d-a68f-86bbdfgT5t.mock.pstmn.io/webhook",
            }
        }


# Linter status result
class AnalysisLinterResultStatus(StrEnum):
    SUCCESS = "success"
    ERROR = "error"


# Linter result
class AnalysisLinterResult(BaseModel):
    requestId: str = Field(
        description="Analysis request id",
        example="530661a2-e266-11ed-9ab4-683e263f13c0",
    )
    status: AnalysisLinterResultStatus = Field(
        description="Status of the linter (success, error)",
        example="success",
    )
    statusMessage: str = Field(
        description="Status message",
        example="No errors were found in the linting process",
    )
    errorNumber: int = Field(
        description="Number of errors found",
        example=8,
    )
    elapsedTime: float = Field(
        description="Elapsed time to run the linter",
        example=1.62,
    )
    descriptorId: str = Field(
        description="MegaLinter descriptor identifier",
        example="PYTHON",
    )
    linterId: str = Field(
        description="MegaLinter linter name",
        example="ruff",
    )
    linterKey: str = Field(
        description="MegaLinter linter key",
        example="PYTHON_RUFF",
    )
    isFormatter: bool = Field(
        description="True if the linter is flagged as a formatter",
        example=True,
    )
    docUrl: str = Field(
        description="URL of the linter documentation on MegaLinter online docs",
        example="https://megalinter.io/latest/descriptors/python_ruff/",
    )
    outputText: str | None = Field(
        default=None,
        description="Console output of the linter process, when available",
        example="",
    )
    outputSarif: object | None = Field(
        default=None,
        description="Sarif output of the linter process, when available",
        example={
            "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
            "runs": [
                {
                    "columnKind": "utf16CodeUnits",
                    "properties": {
                        "megalinter": {
                            "docUrl": "https://megalinter.io/latest/descriptors/repository_devskim",
                            "linterKey": "REPOSITORY_DEVSKIM",
                            "linterVersion": "0.6.5",
                        }
                    },
                    "results": [],
                    "tool": {
                        "driver": {
                            "fullName": "Microsoft DevSkim Command Line Interface",
                            "informationUri": "https://megalinter.io/latest/descriptors/repository_devskim",
                            "name": "devskim (MegaLinter REPOSITORY_DEVSKIM)",
                            "version": "0.6.5+331482234a",
                        }
                    },
                }
            ],
            "version": "2.1.0",
        },
    )


# Full Analysis result
class AnalysisRequest(BaseModel):
    id: str = Field(
        description="Analysis request unique id",
        example="530661a2-e266-11ed-9ab4-683e263f13c0",
    )
    status: AnalysisStatus = Field(
        description="Analysis request status (new,in-progress,complete)",
        example="complete",
    )
    repository: str | None = Field(
        description="Repository used for analysis",
        example="https://github.com/nvuillam/github-dependents-info",
    )
    requestInput: AnalysisRequestInput | None = Field(
        description="Input initially sent that generated this analysis request",
        example={
            "repositoryUrl": "https://github.com/nvuillam/github-dependents-info",
            "webHookUrl": "https://9faea506-7e84-4f5d-a68f-86bbdfgT5t.mock.pstmn.io/webhook",
        },
    )
    snippetLanguage: str | None = Field(
        description="Guessed snippet language",
        example="python",
    )
    results: List[AnalysisLinterResult] = Field(
        default=[], description="All linter analysis results"
    )


class ServerInfo(BaseModel):
    version: str = Field(
        description="Version of MegaLinter Server",
        example="6.21.0",
    )
    runningProcessNumber: int = Field(
        description="Number of currently running analysis",
        example=6,
    )
    maxRunningProcessNumber: int = Field(
        description="Maximum Number of parallel running analysis",
        example=10,
    )
    totalProcessRunNumber: int = Field(
        description="Total Number of analysis since the server has been started",
        example=345,
    )
    available: bool = Field(
        description="Returns true if the server is available (total process number not currently reached)",
        example=True,
    )

    class Config:
        schema_extra = {
            "example": {
                "version": "6.21.0",
                "runningProcessNumber": 4,
                "maxRunningProcessNumber": 10,
                "totalProcessRunNumber": 412,
                "available": True,
            }
        }


# Get status of MegaLinter server
@app.get(
    "/",
    response_model=ServerInfo,
    status_code=status.HTTP_200_OK,
    summary="Returns MegaLinter server version and workload info",
)
async def server_info():
    global running_process_number, max_running_process_number, total_process_number_run
    return {
        "version": app.version,
        "runningProcessNumber": running_process_number,
        "maxRunningProcessNumber": max_running_process_number,
        "totalProcessRunNumber": total_process_number_run,
        "available": running_process_number < max_running_process_number,
    }


# Get info about a request
@app.get(
    "/analysis/{item_id}",
    response_model=AnalysisRequest,
    status_code=status.HTTP_200_OK,
    summary="Returns status (and result if available) of an analysis",
)
async def get_analysis_by_id(item_id):
    global ANALYSIS_EXECUTIONS
    analysis_executor: AnalysisExecutor = AnalysisExecutor.findById(item_id)
    if analysis_executor is not None:
        return analysis_executor.toAnalysisRequest()
    raise HTTPException(
        status_code=404, detail=f"Unable to find analysis request {item_id}"
    )


# Find request by repository url
@app.get(
    "/analysis/",
    response_model=AnalysisRequest,
    status_code=status.HTTP_200_OK,
    summary="Find an existing analysis using repository url as criteria",
)
async def get_analysis_by_repo(repo: str):
    global ANALYSIS_EXECUTIONS
    analysis_executor: AnalysisExecutor = AnalysisExecutor.findByRepository(repo)
    if analysis_executor is not None:
        return analysis_executor.toAnalysisRequest()
    raise HTTPException(
        status_code=404, detail=f"Unable to find analysis request for repository {repo}"
    )


# Post a new request to MegaLinter
@app.post(
    "/analysis",
    response_model=AnalysisRequest,
    status_code=status.HTTP_201_CREATED,
    summary="Requests a new analysis using repository url or snippet",
    description="""If the analysis initialization is successful, an id will be returned.
    If webHookUrl is provided, everytime a linter will be completed, the result will be sent to this HTTP webhook
    """,
)
async def request_analysis(
    background_tasks: BackgroundTasks,
    item: AnalysisRequestInput,
) -> Response:
    # Check server is available
    global running_process_number, max_running_process_number, total_process_number_run
    if running_process_number >= max_running_process_number:
        raise HTTPException(
            status_code=423,
            detail=f"The server is already processing the max number of requests ({max_running_process_number})",
        )
    # Increment number of processing requests
    total_process_number_run += 1
    running_process_number += 1
    analysis_executor = AnalysisExecutor()
    analysis_executor.initialize(item)
    analysis_executor.initialize_files()
    analysis_executor.save()
    background_tasks.add_task(start_analysis, analysis_executor.id)
    return analysis_executor.toAnalysisRequest()


##########################
### Analysis Execution ### # noqa: E266
##########################


# Outside method to start analysis as a background task so HTTP response can be sent before
def start_analysis(analysis_request_id: str):
    analysis_executor: AnalysisExecutor = AnalysisExecutor.findById(analysis_request_id)
    analysis_executor.process()
    global running_process_number
    running_process_number -= 1


# Analysis processor class
class AnalysisExecutor:
    id: str | None = None
    status: AnalysisStatus | None = None
    repository: str | None = None
    request_input: AnalysisRequestInput | None = None
    snippet_language: str | None = None
    workspace: str | None = None
    web_hook_url: str | None = None
    results: List = []

    # Find analysis request from unique id: Could be using external database in the future
    @staticmethod
    def findById(static_analysis_id: str):
        global ANALYSIS_EXECUTIONS
        for analysis_executor in ANALYSIS_EXECUTIONS:
            analysis_executor2: AnalysisExecutor = analysis_executor
            if analysis_executor2.id == static_analysis_id:
                return analysis_executor2
        return None

    # Find analysis request from unique key, like a repository url
    @staticmethod
    def findByRepository(repository: str):
        global ANALYSIS_EXECUTIONS
        for analysis_executor in ANALYSIS_EXECUTIONS:
            analysis_executor2: AnalysisExecutor = analysis_executor
            if analysis_executor2.repository == repository:
                return analysis_executor2
        return None

    # Initialize analysis request and assign an unique Id
    def initialize(self, request_input: AnalysisRequestInput):
        self.id = str(uuid1())
        self.status = AnalysisStatus.NEW
        self.request_input = request_input
        if request_input.webHookUrl:
            self.web_hook_url = request_input.webHookUrl
        logger.info(f"Analysis request {self.id} has been initialized")

    # Initialize files for analysis
    def initialize_files(self):
        # Clone repo from provided url
        if self.request_input.repositoryUrl:
            self.init_from_repository()
            return
        # Detect language and create temporary workspace with file
        elif self.request_input.snippet:
            self.init_from_snippet()
            return
        # Nothing to create a request !
        self.stop_request()
        raise HTTPException(
            status_code=422,
            detail="Unable to initialize files for analysis",  # Unprocessable content
        )

    # Create uniform temp directories
    def create_temp_dir(self):
        return tempfile.mkdtemp(prefix="ct-megalinter-x")

    # Init by cloning a remote repository
    def init_from_repository(self):
        temp_dir = self.create_temp_dir()
        try:
            git.Repo.clone_from(self.request_input.repositoryUrl, temp_dir)
        except Exception as e:
            self.stop_request()
            raise HTTPException(
                status_code=404, detail=f"Unable to clone repository\n{str(e)}"
            )
        logger.info(f"Cloned {self.request_input.repositoryUrl} in temp dir {temp_dir}")
        self.workspace = temp_dir
        self.repository = self.request_input.repositoryUrl

    # Init from user snippet
    def init_from_snippet(self):
        # Guess language using pygments
        code_lexer = lexers.guess_lexer(self.request_input.snippet)
        if not code_lexer:
            self.stop_request()
            raise HTTPException(
                status_code=404, detail="Unable to detect language from snippet"
            )
        self.snippet_language = code_lexer.name
        logger.info(f"Guessed snipped language: {self.snippet_language}")
        # Build file name
        if len(code_lexer.filenames) > 0:
            if "*." in code_lexer.filenames[0]:
                snippet_file_name = "snippet" + code_lexer.filenames[0].replace("*", "")
            else:
                snippet_file_name = code_lexer.filenames[0]
        else:
            self.stop_request()
            raise HTTPException(
                status_code=404,
                detail=f"Unable build file from {code_lexer.name} snippet",
            )
        logger.info(f"Snippet file name: {snippet_file_name}")
        temp_dir = self.create_temp_dir()
        snippet_file = os.path.join(temp_dir, snippet_file_name)
        with open(snippet_file, "w", encoding="utf-8") as file:
            file.write(self.request_input.snippet)
        self.workspace = temp_dir

    # Build result for output
    def toAnalysisRequest(self):
        analysis_request = AnalysisRequest(
            id=self.id,
            status=self.status,
            repository=self.repository,
            requestInput=self.request_input,
        )
        if self.repository:
            analysis_request.repository = self.repository
        if self.snippet_language:
            analysis_request.snippetLanguage = self.snippet_language
        if len(self.results) > 0:
            analysis_request.results = self.results
        return analysis_request

    # Stop request and release a slot for a next request
    def stop_request(self):
        global running_process_number
        running_process_number -= 1

    # Change status of analysis request
    def change_status(self, status: AnalysisStatus):
        self.status = status
        logger.info(f"Analysis request {self.id} status change: {status}")
        self.save()

    # Save state of Analysis Request (Could be using external database in the future)
    def save(self):
        global ANALYSIS_EXECUTIONS
        existing_analysis_request = AnalysisExecutor.findById(self.id)
        if existing_analysis_request is not None:
            for index, x in enumerate(ANALYSIS_EXECUTIONS):
                if x.id == self.id:
                    ANALYSIS_EXECUTIONS[index] = self
                    break
        else:
            ANALYSIS_EXECUTIONS.append(self)
        logger.info(f"Analysis request {self.id} has been saved")

    # Run MegaLinter
    def process(self):
        mega_linter = MegaLinter.Megalinter(
            {
                "cli": False,
                "request_id": self.id,
                "workspace": self.workspace,
                "SARIF_REPORTER": "true",
                "WEBHOOK_REPORTER": "true",
                "WEBHOOK_REPORTER_URL": self.web_hook_url,
            }
        )
        self.change_status(AnalysisStatus.IN_PROGRESS)
        mega_linter.run()
        for linters in mega_linter.linters:
            for reporter in linters.reporters:
                if reporter.name == "WEBHOOK_REPORTER" and reporter.web_hook_data:
                    self.results.append(reporter.web_hook_data)
        self.change_status(AnalysisStatus.COMPLETE)
        del mega_linter
