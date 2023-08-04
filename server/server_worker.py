import glob
import logging
import os
import shutil
import tempfile
import zipfile
from typing import List

import git
from megalinter import MegaLinter
from pygments import lexers
from server.errors import MegalinterServerException
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
        logger.info(f"Analysis request {self.id} has been initialized")

    # Initialize files for analysis
    def initialize_files(self):
        # Clone repo from provided url
        if self.request_input.repositoryUrl:
            self.init_from_repository()
            return
        # Use uploaded files
        elif self.request_input.fileUploadId:
            self.init_from_file_upload(self.request_input.fileUploadId)
            return
        # Detect language and create temporary workspace with file
        elif self.request_input.snippet:
            self.init_from_snippet()
            return
        # Nothing to create a request !
        err = MegalinterServerException(
            "Unable to initialize files for analysis",
            "missingAnalysisType",
            self.id,
            {"request_input": self.request_input},
        )
        err.send_redis_message()
        raise err

    # Init by cloning a remote repository
    def init_from_repository(self):
        temp_dir = self.create_temp_dir()
        try:
            git.Repo.clone_from(self.request_input.repositoryUrl, temp_dir)
        except Exception as e:
            err = MegalinterServerException(
                f"Unable to clone repository {self.request_input.repositoryUrl}",
                "gitCloneError",
                self.id,
                {"error": str(e)},
            )
            err.send_redis_message()
            raise err
        logger.info(f"Cloned {self.request_input.repositoryUrl} in temp dir {temp_dir}")
        self.workspace = temp_dir
        self.repository = self.request_input.repositoryUrl

    # Init by getting uploaded file(s)
    def init_from_file_upload(self, file_upload_id):
        temp_dir = self.create_temp_dir()
        upload_dir = os.path.join("/tmp/server-files", file_upload_id)
        if os.path.exists(upload_dir):
            zip_files = glob.glob(upload_dir + "/*.zip")
            if len(zip_files) == 1:
                # Unique zip file
                with zipfile.ZipFile(zip_files[0], "r") as zip_ref:
                    zip_ref.extractall(temp_dir)
            else:
                # No zip file
                shutil.copytree(upload_dir, temp_dir, dirs_exist_ok=True)
            logger.info(f"Copied uploaded files from {self.id} in temp dir {temp_dir}")
            self.workspace = temp_dir
            self.repository = self.request_input.repositoryUrl
        else:
            err = MegalinterServerException(
                "Unable to load uploaded files for analysis",
                "uploadedFileNotFound",
                self.id,
                {"file_upload_id": file_upload_id},
            )
            err.send_redis_message()
            raise err

    # Init from user snippet
    def init_from_snippet(self):
        logger.info(f"Input snippet:\n {self.request_input.snippet}")
        if self.request_input.snippetExtension:
            snippet_file_name = "snippet" + self.request_input.snippetExtension
        elif self.request_input.snippetLanguage:
            snippet_file_name = self.get_language_extension()
        else:
            snippet_file_name = self.guess_snippet_filename()
        logger.info(f"Snippet file name: {snippet_file_name}")
        temp_dir = self.create_temp_dir()
        snippet_file = os.path.join(temp_dir, snippet_file_name)
        with open(snippet_file, "w", encoding="utf-8") as file:
            file.write(self.request_input.snippet)
        self.workspace = temp_dir

    # Get extension from language
    def get_language_extension(self):
        languageId = self.request_input.snippetLanguage
        all_code_lexers = lexers.get_all_lexers()
        code_lexer_name = None
        code_lexer_filenames = None
        for name, aliases, filenames, _mimetypes in all_code_lexers:
            if name == languageId or name in aliases:
                code_lexer_name = name
                code_lexer_filenames = filenames
                break
        if code_lexer_name is None:
            err = MegalinterServerException(
                "Unable to find pygments language for " + languageId,
                "snippetUnknownLanguage",
                self.id,
                {"snippet": self.request_input.snippet, "snippetLanguage": languageId},
            )
            err.send_redis_message()
            raise err
        logger.info(f"Identified snippet language: {code_lexer_name}")
        # Build file name
        if len(code_lexer_filenames) > 0:
            if "*." in code_lexer_filenames[0]:
                snippet_file_name = "snippet" + code_lexer_filenames[0].replace("*", "")
            else:
                snippet_file_name = code_lexer_filenames[0]
        else:
            err = MegalinterServerException(
                f"Unable build file from {code_lexer_name} snippet",
                "snippetBuildError",
                self.id,
                {"snippet": self.request_input.snippet},
            )
            err.send_redis_message()
            raise err
        return snippet_file_name

    # Guess language using pygments
    def guess_snippet_filename(self):
        code_lexer = lexers.guess_lexer(self.request_input.snippet)
        if not code_lexer:
            err = MegalinterServerException(
                "Unable to detect language from snippet",
                "snippetGuessError",
                self.id,
                {"snippet": self.request_input.snippet},
            )
            err.send_redis_message()
            raise err
        self.snippet_language = code_lexer.name
        logger.info(f"Guessed snipped language: {self.snippet_language}")
        # Build file name
        if len(code_lexer.filenames) > 0:
            if "*." in code_lexer.filenames[0]:
                snippet_file_name = "snippet" + code_lexer.filenames[0].replace("*", "")
            else:
                snippet_file_name = code_lexer.filenames[0]
        else:
            err = MegalinterServerException(
                f"Unable build file from {code_lexer.name} snippet",
                "snippetBuildError",
                self.id,
                {"snippet": self.request_input.snippet},
            )
            err.send_redis_message()
            raise err
        return snippet_file_name

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
        logger.debug("Saved state " + str(self.__dict__))
