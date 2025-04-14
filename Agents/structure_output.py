from typing import List

from pydantic import BaseModel, Field


class BaseOutput(BaseModel):
    Title: str = Field(description="Title of the request")
    Description: str = Field(description="The description of the request")


class ValidationOutput(BaseOutput):
    Reformulated: str = Field(description="The project idea reformulated for a better understanding if needed")


class IssueOutput(BaseOutput):
    Title: str = Field(description="Title of the issue with prefix feat: or bug: or doc:")
    Description: str = Field(description="The description of the functionality or the bug")
    Labels: List[str] = Field(description="A list of github labels that correspond to the issue")


class IssuesOutput(BaseModel):
    Issues: List[IssueOutput] = Field(description="A list of issues that are created")
