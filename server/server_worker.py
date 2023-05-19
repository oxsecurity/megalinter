import os

from fastapi import HTTPException
import git
from server.types import AnalysisRequestInput, AnalysisStatus
from pygments import lexers

def processAnalysisRequest(
    item,
    request_id,
    server_id,
):
    analysis_executor = MegaLinterAnalysis()
    analysis_executor.initialize(item, request_id, server_id)
    return {}


# Analysis processor class
class MegaLinterAnalysis:
    id: str | None = None
    server_id: str | None = None
    status: AnalysisStatus | None = None
    repository: str | None = None
    snippet_language: str | None = None
    workspace: str | None = None
    web_hook_url: str | None = None

    # Initialize analysis request and assign an unique Id
    def initialize(self, request_input: AnalysisRequestInput, request_id, server_id):
        self.id = (request_id,)
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
