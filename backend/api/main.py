import asyncio
import logging
from contextlib import asynccontextmanager
from typing import List, Optional
from uuid import uuid4

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel, Field

from core.types import Project, ProjectStatus, ReportSection, WorkflowEvent, AgentType
from core.orchestrator import Orchestrator
from services.pdf_service import get_pdf_service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CreateProjectRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    query: str = Field(..., min_length=10)
    description: str = ""


class UpdateSectionRequest(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None


orchestrator = Orchestrator()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Market Research Orchestrator API")
    yield
    logger.info("Shutting down Market Research Orchestrator API")


app = FastAPI(
    title="Multi-Agent Market Research API",
    description="Orchestration system for AI-powered market research",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {
        "message": "Multi-Agent Market Research System API",
        "version": "1.0.0",
        "status": "operational"
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy", "agents": [a.value for a in orchestrator.agent_registry.list_agents()]}


@app.post("/projects", response_model=Project)
async def create_project(request: CreateProjectRequest):
    """Create a new research project."""
    project = await orchestrator.create_project(
        title=request.title,
        query=request.query,
        description=request.description
    )
    return project


@app.get("/projects", response_model=List[Project])
async def list_projects():
    """List all projects."""
    return orchestrator.list_projects()


@app.get("/projects/{project_id}", response_model=Project)
async def get_project(project_id: str):
    """Get a specific project by ID."""
    project = orchestrator.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@app.delete("/projects/{project_id}")
async def delete_project(project_id: str):
    """Delete a project."""
    project = orchestrator.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    del orchestrator._projects[project_id]
    return {"message": "Project deleted successfully"}


@app.post("/projects/{project_id}/execute")
async def execute_workflow(project_id: str, background_tasks: BackgroundTasks):
    """Execute the research and writing workflow for a project."""
    project = orchestrator.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if project.status not in [ProjectStatus.DRAFT, ProjectStatus.FAILED]:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot execute workflow from status: {project.status.value}"
        )
    
    async def run_workflow():
        try:
            await orchestrator.execute_workflow(project_id)
        except Exception as e:
            logger.error(f"Workflow error: {e}")
            project.status = ProjectStatus.FAILED
    
    background_tasks.add_task(run_workflow)
    
    return {
        "message": "Workflow execution started",
        "project_id": project_id,
        "status": "in_progress"
    }


@app.post("/projects/{project_id}/research")
async def execute_research_phase(project_id: str):
    """Execute only the research phase."""
    project = orchestrator.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if project.status == ProjectStatus.RESEARCHING:
        raise HTTPException(status_code=400, detail="Research already in progress")
    
    try:
        research_task = await orchestrator.execute_research_phase(project)
        return {
            "message": "Research phase completed",
            "sources_count": len(research_task.sources),
            "gaps": research_task.gaps
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/projects/{project_id}/write")
async def execute_writing_phase(project_id: str):
    """Execute only the writing phase."""
    project = orchestrator.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if not project.research_task or project.research_task.status != "completed":
        raise HTTPException(status_code=400, detail="Research must be completed first")
    
    try:
        writing_tasks = await orchestrator.execute_writing_phase(project)
        return {
            "message": "Writing phase completed",
            "sections_completed": len([t for t in writing_tasks if t.status.value == "completed"])
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/projects/{project_id}/events", response_model=List[WorkflowEvent])
async def get_project_events(project_id: str):
    """Get workflow events for a project."""
    events = orchestrator.get_events(project_id)
    return events


@app.get("/projects/{project_id}/sources")
async def get_project_sources(project_id: str):
    """Get research sources for a project."""
    project = orchestrator.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if not project.research_task:
        return {"sources": [], "message": "No research task completed"}
    
    return {
        "sources": [
            {
                "id": s.id,
                "title": s.title,
                "url": s.url,
                "credibility_score": s.credibility_score
            }
            for s in project.research_task.sources
        ]
    }


@app.patch("/projects/{project_id}/sections/{section_id}")
async def update_section(project_id: str, section_id: str, request: UpdateSectionRequest):
    """Update a section's content."""
    project = orchestrator.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    section = next((s for s in project.sections if s.id == section_id), None)
    if not section:
        raise HTTPException(status_code=404, detail="Section not found")
    
    if request.title:
        section.title = request.title
    if request.content is not None:
        section.content = request.content
    
    project.updated_at = project.updated_at
    
    return section


@app.get("/projects/{project_id}/export/pdf")
async def export_pdf(project_id: str):
    """Export project as PDF."""
    project = orchestrator.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if project.status != ProjectStatus.COMPLETED:
        raise HTTPException(
            status_code=400,
            detail="Project must be completed before export"
        )
    
    if not project.sections:
        raise HTTPException(status_code=400, detail="No content to export")
    
    pdf_service = get_pdf_service()
    pdf_bytes = pdf_service.generate_pdf(project)
    
    filename = f"{project.title.replace(' ', '_')}_report.pdf"
    
    return StreamingResponse(
        iter([pdf_bytes]),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
