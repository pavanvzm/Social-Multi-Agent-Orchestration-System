from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID, uuid4


class AgentType(str, Enum):
    RESEARCH = "research"
    WRITER = "writer"
    PLANNING = "planning"
    REVIEWER = "reviewer"


class TaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class ProjectStatus(str, Enum):
    DRAFT = "draft"
    RESEARCHING = "researching"
    WRITING = "writing"
    REVIEWING = "reviewing"
    COMPLETED = "completed"
    FAILED = "failed"


class Source(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    title: str
    url: Optional[str] = None
    credibility_score: float = Field(default=0.5, ge=0.0, le=1.0)
    content: Optional[str] = None
    scraped_at: datetime = Field(default_factory=datetime.now)


class ReportSection(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    title: str
    content: str = ""
    order: int
    sources: List[str] = Field(default_factory=list)
    confidence_score: float = Field(default=0.0, ge=0.0, le=1.0)
    status: TaskStatus = TaskStatus.PENDING


class ResearchTask(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    query: str
    status: TaskStatus = TaskStatus.PENDING
    sources: List[Source] = Field(default_factory=list)
    gaps: List[str] = Field(default_factory=list)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error: Optional[str] = None


class WritingTask(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    section_id: str
    research_task_id: str
    status: TaskStatus = TaskStatus.PENDING
    content: str = ""
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error: Optional[str] = None


class Project(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    title: str
    description: str = ""
    query: str
    status: ProjectStatus = ProjectStatus.DRAFT
    sections: List[ReportSection] = Field(default_factory=list)
    research_task: Optional[ResearchTask] = None
    writing_tasks: List[WritingTask] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class AgentResponse(BaseModel):
    agent_type: AgentType
    task_id: str
    status: TaskStatus
    progress: float = Field(default=0.0, ge=0.0, le=1.0)
    message: str = ""
    data: Optional[Dict[str, Any]] = None


class WorkflowEvent(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    project_id: str
    agent_type: AgentType
    event_type: str
    message: str
    timestamp: datetime = Field(default_factory=datetime.now)
    data: Optional[Dict[str, Any]] = None
