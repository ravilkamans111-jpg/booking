from typing import Annotated
from fastapi import Depends
from pydantic import BaseModel, Field


class PaginationParams(BaseModel):
    limit: int = Field(5, ge=1, le=100, description="Page size")
    offset: int = Field(0, ge=0, description="Offset")


PaginationDep = Annotated[PaginationParams, Depends(PaginationParams)]
