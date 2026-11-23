from pydantic import BaseModel , Field
class ResearchSummary(BaseModel):
    title:str=Field(description="The title of the research paper")
    key_points:list[str]=Field(description="A list of key points from the research paper")
    sources:str=Field(description="The sources of the research paper")