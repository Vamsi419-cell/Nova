from pydantic import BaseModel,Field
from typing import Optional,Literal
class caliculator_val(BaseModel):
    expression:str
class whether_val(BaseModel):
    location:str=Field(description="The location for which to get the weather")
    units:Literal["celsius","fahrenheit"]= Field(default="celsius",description="The units for the temperature"
    )
class websearch_val(BaseModel):
    query:str
class caliculator_output(BaseModel):
    result:float
class whether_output(BaseModel):
    result:str
class websearch_output(BaseModel):
    result:str