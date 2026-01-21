"""
Pydantic Models for API Request/Response Schemas
Defines the data structures for all API endpoints.
"""

from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel, Field


# ===========================================
# Health Check
# ===========================================

class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    app_name: str
    version: str
    document_count: int
    llm_provider: str
    llm_model: str


# ===========================================
# Chat Endpoint Models
# ===========================================

class BusinessContext(BaseModel):
    """Optional business context for personalized privilege matching."""
    industry: Optional[str] = Field(None, description="Business industry (IT, Agriculture, Manufacturing, etc.)")
    employee_count: Optional[int] = Field(None, ge=0, description="Number of employees")
    annual_revenue: Optional[float] = Field(None, ge=0, description="Annual revenue in UZS")
    region: Optional[str] = Field(None, description="Business location (Toshkent, Samarqand, etc.)")
    years_in_operation: Optional[int] = Field(None, ge=0, description="Years since business was established")


class ChatRequest(BaseModel):
    """Request body for chat endpoint."""
    message: str = Field(..., min_length=1, max_length=2000, description="User's question in Uzbek or Russian")
    business_context: Optional[BusinessContext] = Field(None, description="Optional business info for better matching")
    conversation_id: Optional[str] = Field(None, description="Conversation ID for multi-turn context")


class DocumentSource(BaseModel):
    """Source document information."""
    title: str
    document_id: str = Field(..., description="Decree identifier (e.g., PQ-60)")
    url: Optional[str] = None
    relevance_score: float = Field(..., ge=0, le=1)
    excerpt: str = Field(..., description="Relevant text excerpt")


class MatchedPrivilege(BaseModel):
    """A specific privilege matched to the user's query."""
    name: str
    privilege_type: Literal["grant", "subsidy", "tax_holiday", "loan", "other"]
    eligibility: Optional[str] = None
    deadline: Optional[str] = None
    amount: Optional[str] = None


class ChatResponse(BaseModel):
    """Response from the chat endpoint."""
    response: str = Field(..., description="AI-generated answer")
    sources: list[DocumentSource] = Field(default_factory=list)
    matched_privileges: list[MatchedPrivilege] = Field(default_factory=list)
    conversation_id: str
    timestamp: datetime = Field(default_factory=datetime.now)


# ===========================================
# Scout Agent Models
# ===========================================

class ScoutStatusDetails(BaseModel):
    """Details for scout status events."""
    document_id: Optional[str] = None
    title: Optional[str] = None
    url: Optional[str] = None
    relevance: Optional[bool] = None
    progress: int = Field(0, ge=0, le=100)


class ScoutStatusEvent(BaseModel):
    """Real-time status event from Scout Agent."""
    event_type: Literal["search", "judge", "ingest", "complete", "error"]
    message: str
    details: ScoutStatusDetails = Field(default_factory=ScoutStatusDetails)
    timestamp: datetime = Field(default_factory=datetime.now)


class ScoutTriggerRequest(BaseModel):
    """Request to manually trigger Scout Agent."""
    keywords: Optional[list[str]] = Field(None, description="Override default search keywords")
    date_filter: Optional[str] = Field(None, description="Date filter (e.g., 'after:2025-01-01')")
    force_refresh: bool = Field(False, description="Re-process already indexed documents")


class ScoutTriggerResponse(BaseModel):
    """Response after triggering Scout Agent."""
    status: Literal["started", "already_running"]
    job_id: str
    message: str
    estimated_duration_seconds: int = Field(default=60)
