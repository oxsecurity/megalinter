# mypy: ignore-errors
# Analysis status enum
from enum import StrEnum

from pydantic import BaseModel, Field

# API types


# Analysis request model
class AnalysisRequestInput(BaseModel):
    class Config:
        schema_extra = {
            "example": {
                "repositoryUrl": "https://github.com/nvuillam/github-dependents-info",
                "webHookUrl": "https://9faea506-7e84-4f5d-a68f-86bbdfgT5t.mock.pstmn.io/webhook",
            }
        }

    fileUploadId: str | None = Field(
        default=None,
        description="Id of the file upload previously run",
        example="xxx123",
    )
    snippet: str | None = Field(
        default=None,
        description="Input any code snippet",
        example="#!/usr/bin/env python3",
    )
    snippetLanguage: str | None = Field(
        default=None,
        description=(
            "Language of code snippet (must be a pygments name"
            + " or shortname: https://pygments.org/languages/)"
        ),
        example="PYTHON",
    )
    snippetExtension: str | None = Field(
        default=None,
        description="Extension of code snippet",
        example=".py",
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


# Analysis request output
class AnalysisRequestOutput(BaseModel):
    class Config:
        arbitrary_types_allowed = True

    request_id: str | None = (
        Field(  # type: ignore
            description="Unique identifier of the request",
            example="",
        ),
    )
    server_id: str | None = Field(
        description="Unique identifier of the server",
        example="",
    )
    job_id: str | None = Field(
        description="Unique identifier of the queues job",
        example="",
    )


class AnalysisStatus(StrEnum):
    NEW = "new"
    IN_PROGRESS = "in-progress"
    COMPLETE = "complete"
