from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ReferenceItem(BaseModel):
    document_name: str = Field(..., description="Document identifier, e.g. 'IRP 5'")
    title: Optional[str] = Field(None, description="Document title")
    author: Optional[str] = Field(None, description="Author names")
    year: Optional[int] = Field(None, description="Publication year")
    publisher: Optional[str] = Field(None, description="Publisher name")
    document_type: Optional[str] = Field(None, description="Document classification")
    source_url: Optional[str] = Field(None, description="Verbatim source URL on ifikr.my")
    section: Optional[str] = Field(None, description="Section header path")
    chunk_id: Optional[str] = Field(None, description="Unique chunk identifier")


class AgentResponse(BaseModel):
    result: str = Field(..., description="Sanitized scholarly markdown response")
    references: List[ReferenceItem] = Field(default_factory=list, description="Structured citation references")
    json_output: Dict[str, Any] = Field(default_factory=dict, description="Machine-readable structured payload")
