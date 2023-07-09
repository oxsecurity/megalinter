import logging
import os
import tempfile
from typing import List

import git
from fastapi import HTTPException
from megalinter import MegaLinter
from pygments import lexers
from server.types import AnalysisRequestInput, AnalysisStatus

logger = logging.getLogger(__name__)


def processAnalysisRequest(
    request_input: dict,
    request_id: str,
    server_id: str,
):
    analysis = MegaLinterAnalysis()
    analysis.initialize(
        AnalysisRequestInput.parse_obj(request_input), request_id, server_id
    )
    analysis.initialize_files()
    analysis.process()
    return analysis.__dict__


# Analysis processor class
class MegaLinterAnalysis:
    id: str | None = None
    server_id: str | None = None
    status: AnalysisStatus | None = None
    repository: str | None = None
    snippet_language: str | None = None
    workspace: str | None = None
    web_hook_url: str | None = None
    results: List = []

    # Initialize analysis request and assign an unique Id
    def initialize(self, request_input: AnalysisRequestInput, request_id, server_id):
        self.id = request_id
        self.server_id = server_id
        self.status = AnalysisStatus.NEW
        self.request_input = request_input
        if request_input.webHookUrl:
            self.web_hook_url = request_input.webHookUrl
        print(f"Analysis request {self.id} has been initialized")

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
        raise HTTPException(
            status_code=422,
            detail="Unable to initialize files for analysis",  # Unprocessable content
        )

    # Init by cloning a remote repository
    def init_from_repository(self):
        temp_dir = self.create_temp_dir()
        try:
            git.Repo.clone_from(self.request_input.repositoryUrl, temp_dir)
        except Exception as e:
            raise HTTPException(
                status_code=404, detail=f"Unable to clone repository\n{str(e)}"
            )
        print(f"Cloned {self.request_input.repositoryUrl} in temp dir {temp_dir}")
        self.workspace = temp_dir
        self.repository = self.request_input.repositoryUrl

    # Init from user snippet
    def init_from_snippet(self):
        # Guess language using pygments
        code_lexer = lexers.guess_lexer(self.request_input.snippet)
        if not code_lexer:
            raise HTTPException(
                status_code=404, detail="Unable to detect language from snippet"
            )
        self.snippet_language = code_lexer.name
        print(f"Guessed snipped language: {self.snippet_language}")
        # Build file name
        if len(code_lexer.filenames) > 0:
            if "*." in code_lexer.filenames[0]:
                snippet_file_name = "snippet" + code_lexer.filenames[0].replace("*", "")
            else:
                snippet_file_name = code_lexer.filenames[0]
        else:
            raise HTTPException(
                status_code=404,
                detail=f"Unable build file from {code_lexer.name} snippet",
            )
        print(f"Snippet file name: {snippet_file_name}")
        temp_dir = self.create_temp_dir()
        snippet_file = os.path.join(temp_dir, snippet_file_name)
        with open(snippet_file, "w", encoding="utf-8") as file:
            file.write(self.request_input.snippet)
        self.workspace = temp_dir

    # Run MegaLinter
    def process(self):
        megalinter_params = {
            "cli": False,
            "request_id": self.id,
            "workspace": self.workspace,
            "SARIF_REPORTER": "true",
        }
        if self.web_hook_url:
            megalinter_params["WEBHOOK_REPORTER"] = "true"
            megalinter_params["WEBHOOK_REPORTER_URL"] = self.web_hook_url
        mega_linter = MegaLinter.Megalinter(megalinter_params)
        self.change_status(AnalysisStatus.IN_PROGRESS)
        mega_linter.run()
        for linters in mega_linter.linters:
            for reporter in linters.reporters:
                if reporter.name == "WEBHOOK_REPORTER" and reporter.web_hook_data:
                    self.results.append(reporter.web_hook_data)
        self.change_status(AnalysisStatus.COMPLETE)
        del mega_linter

    # Create uniform temp directories
    def create_temp_dir(self):
        return tempfile.mkdtemp(prefix="ct-megalinter-x")

    # Change status of analysis request
    def change_status(self, status: AnalysisStatus):
        self.status = status
        logger.info(f"Analysis request {self.id} status change: {status}")
        self.save()

    def save(self):
        print("Saved state " + str(self.__dict__))
