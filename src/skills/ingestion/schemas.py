from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class DocumentMetadata(BaseModel):
    document_name: str = Field(..., description="Unique document slug / ID (e.g. 'ARXIV_2401_001')")
    title: str = Field(..., description="Full title of the publication")
    author: Optional[str] = Field(None, description="Author names or organization")
    year: Optional[int] = Field(None, description="Publication year")
    publisher: Optional[str] = Field("arXiv", description="Publisher or repository")
    document_type: Optional[str] = Field("Research Paper", description="Document type")
    source_url: Optional[str] = Field(None, description="Canonical source URL or file reference")


class IngestionChunk(BaseModel):
    chunk_id: str = Field(..., description="Unique chunk identifier")
    document_name: str = Field(..., description="Parent document identifier")
    header_path: str = Field(..., description="Hierarchical breadcrumb path")
    chunk_content: str = Field(..., description="Cleaned passage content")
    word_count: Optional[int] = Field(None, description="Passage word count")


class EvaluationProbe(BaseModel):
    probe_id: str
    target_header_path: str
    query_text: str
    variation_idx: int


class EvaluationResult(BaseModel):
    total_probes: int
    successful_retrievals: int
    recall_score: float
    passed: bool
    failing_sections: List[str] = Field(default_factory=list)
    diagnostic_logs: List[Dict[str, Any]] = Field(default_factory=list)


class IngestionReport(BaseModel):
    document_metadata: DocumentMetadata
    status: str = Field(..., description="'SUCCESS', 'QUARANTINED', or 'ERROR'")
    total_chunks: int = 0
    final_recall_score: float = 0.0
    iterations_used: int = 1
    quarantine_reason: Optional[str] = None

