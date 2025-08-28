from typing import List, Optional
from pydantic import BaseModel, Field

class SpyCatCreate(BaseModel):
    name: str = Field(..., min_length=1)
    years_of_experience: int = Field(..., ge=0)
    breed: str = Field(..., min_length=1)
    salary: float = Field(..., gt=0)

class SpyCatUpdate(BaseModel):
    salary: float = Field(..., gt=0)

class SpyCatResponse(BaseModel):
    id: int
    name: str
    years_of_experience: int
    breed: str
    salary: float
    
    class Config:
        from_attributes = True

class TargetCreate(BaseModel):
    name: str = Field(..., min_length=1)
    country: str = Field(..., min_length=1)
    notes: str = ""

class TargetResponse(BaseModel):
    id: int
    name: str
    country: str
    notes: str
    complete: bool
    
    class Config:
        from_attributes = True

class TargetNotesUpdate(BaseModel):
    notes: str = Field(..., min_length=0)

class MissionCreate(BaseModel):
    targets: List[TargetCreate] = Field(..., min_items=1, max_items=3) # type: ignore

class MissionResponse(BaseModel):
    id: int
    cat_id: Optional[int]
    complete: bool
    targets: List[TargetResponse]
    
    class Config:
        from_attributes = True