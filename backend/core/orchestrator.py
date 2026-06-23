import asyncio
import logging
from typing import Dict, List, Optional, Callable
from datetime import datetime
from uuid import uuid4

from core.types import (
    Project,
    ProjectStatus,
    TaskStatus,
    AgentType,
    ReportSection,
    ResearchTask,
    WritingTask,
    WorkflowEvent,
)

logger = logging.getLogger(__name__)


class AgentRegistry:
    def __init__(self):
        self._agents: Dict[AgentType, Callable] = {}
    
    def register(self, agent_type: AgentType, agent_handler: Callable):
        self._agents[agent_type] = agent_handler
        logger.info(f"Registered agent: {agent_type.value}")
    
    def get(self, agent_type: AgentType) -> Optional[Callable]:
        return self._agents.get(agent_type)
    
    def list_agents(self) -> List[AgentType]:
        return list(self._agents.keys())


class WorkflowEngine:
    def __init__(self, agent_registry: AgentRegistry):
        self.agent_registry = agent_registry
        self._event_handlers: Dict[str, List[Callable]] = {}
        self._active_tasks: Dict[str, asyncio.Task] = {}
    
    async def execute_research_phase(self, project: Project) -> ResearchTask:
        logger.info(f"Starting research phase for project: {project.id}")
        
        research_task = ResearchTask(
            id=str(uuid4()),
            query=project.query,
            status=TaskStatus.IN_PROGRESS,
            started_at=datetime.now()
        )
        project.research_task = research_task
        project.status = ProjectStatus.RESEARCHING
        
        await self._emit_event(project.id, AgentType.RESEARCH, "started", "Research phase initiated")
        
        research_agent = self.agent_registry.get(AgentType.RESEARCH)
        if research_agent:
            try:
                result = await research_agent(research_task)
                research_task.sources = result.get("sources", [])
                research_task.gaps = result.get("gaps", [])
                research_task.status = TaskStatus.COMPLETED
                research_task.completed_at = datetime.now()
                await self._emit_event(
                    project.id, AgentType.RESEARCH, "completed",
                    f"Research completed with {len(research_task.sources)} sources"
                )
            except Exception as e:
                logger.error(f"Research agent error: {e}")
                research_task.status = TaskStatus.FAILED
                research_task.error = str(e)
                await self._emit_event(project.id, AgentType.RESEARCH, "failed", str(e))
        else:
            logger.warning("Research agent not registered, using simulated data")
            await self._simulate_research(research_task)
        
        return research_task
    
    async def _simulate_research(self, research_task: ResearchTask) -> None:
        await asyncio.sleep(2)
        from core.types import Source
        research_task.sources = [
            Source(
                title="Industry Report 2026",
                url="https://example.com/industry-report",
                credibility_score=0.9,
                content="Key market insights and trends for the industry."
            ),
            Source(
                title="Market Analysis Quarterly",
                url="https://example.com/market-analysis",
                credibility_score=0.85,
                content="Quarterly analysis of market dynamics and competitive landscape."
            ),
            Source(
                title="Competitor Overview",
                url="https://example.com/competitors",
                credibility_score=0.8,
                content="Detailed competitive analysis and market positioning."
            ),
        ]
        research_task.gaps = ["Customer survey data unavailable"]
        research_task.status = TaskStatus.COMPLETED
        research_task.completed_at = datetime.now()
    
    async def execute_writing_phase(self, project: Project) -> List[WritingTask]:
        logger.info(f"Starting writing phase for project: {project.id}")
        
        project.status = ProjectStatus.WRITING
        await self._emit_event(project.id, AgentType.WRITER, "started", "Writing phase initiated")
        
        if not project.sections:
            project.sections = await self._generate_outline(project)
        
        writing_tasks: List[WritingTask] = []
        
        writer_agent = self.agent_registry.get(AgentType.WRITER)
        
        for section in project.sections:
            writing_task = WritingTask(
                id=str(uuid4()),
                section_id=section.id,
                research_task_id=project.research_task.id if project.research_task else "",
                status=TaskStatus.IN_PROGRESS,
                started_at=datetime.now()
            )
            project.writing_tasks.append(writing_task)
            writing_tasks.append(writing_task)
            
            if writer_agent:
                try:
                    result = await writer_agent(writing_task, section, project.research_task)
                    writing_task.content = result.get("content", "")
                    writing_task.status = TaskStatus.COMPLETED
                    section.content = writing_task.content
                    section.status = TaskStatus.COMPLETED
                    section.confidence_score = result.get("confidence", 0.8)
                    await self._emit_event(
                        project.id, AgentType.WRITER, "section_completed",
                        f"Section '{section.title}' completed"
                    )
                except Exception as e:
                    logger.error(f"Writer agent error: {e}")
                    writing_task.status = TaskStatus.FAILED
                    writing_task.error = str(e)
                    await self._emit_event(project.id, AgentType.WRITER, "failed", str(e))
            else:
                await self._simulate_writing(writing_task, section)
                section.content = writing_task.content
                section.status = TaskStatus.COMPLETED
        
        project.status = ProjectStatus.COMPLETED
        await self._emit_event(project.id, AgentType.WRITER, "completed", "All sections written")
        
        return writing_tasks
    
    async def _simulate_writing(self, writing_task: WritingTask, section: ReportSection) -> None:
        await asyncio.sleep(1.5)
        section_templates = {
            "Executive Summary": """The {query} analysis reveals significant market dynamics that require strategic attention. This comprehensive report examines key factors influencing market performance and provides actionable insights for stakeholders. Our research indicates strong potential for growth in the identified segments, with particular emphasis on emerging opportunities in technology adoption and consumer behavior shifts. The findings suggest a favorable environment for strategic investments, though careful consideration of competitive pressures remains essential.""",
            "Company Overview": """This section provides a detailed examination of the company's position within the broader market context. Based on extensive research, the organization demonstrates established market presence with diversified revenue streams. Key strengths include robust operational capabilities and strategic partnerships that enhance competitive positioning. The company's approach to market challenges reflects adaptive strategies aligned with evolving industry demands.""",
            "Market Analysis": """The market landscape presents both opportunities and challenges that merit careful analysis. Current market conditions indicate sustained demand across key segments, with growth projections supporting positive outlook. Competitive dynamics suggest increased activity in innovation and market expansion efforts. Industry trends point toward continued evolution in consumer preferences and technological integration.""",
            "Competitive Landscape": """The competitive environment features several key players vying for market share in an increasingly dynamic space. Analysis of competitor strategies reveals common themes around product innovation and customer experience enhancement. Market positioning varies across players, with differentiation occurring through specialized offerings and geographic expansion. Emerging competitors continue to disrupt traditional market assumptions.""",
            "Recommendations": """Based on our comprehensive analysis, we recommend a multi-faceted approach that addresses both immediate opportunities and long-term strategic positioning. Key priorities include accelerating digital transformation initiatives, strengthening customer engagement programs, and exploring strategic partnerships. Resource allocation should favor high-impact initiatives with clear ROI potential. Regular review and adjustment of strategies will be essential as market conditions evolve."""
        }
        
        template = section_templates.get(section.title, 
            f"""This section addresses {section.title.lower()} based on our research findings. """
            f"""Analysis of available data indicates key trends and patterns that inform strategic decision-making. """
            f"""The research phase uncovered {len(project_research_context())} relevant sources that inform this analysis. """)
        
        writing_task.content = template
        writing_task.status = TaskStatus.COMPLETED
        writing_task.completed_at = datetime.now()


def project_research_context():
    return "comprehensive market"


async def _generate_outline(self, project: Project) -> List[ReportSection]:
    outline = [
        ReportSection(title="Executive Summary", order=0),
        ReportSection(title="Company Overview", order=1),
        ReportSection(title="Market Analysis", order=2),
        ReportSection(title="Competitive Landscape", order=3),
        ReportSection(title="Recommendations", order=4),
    ]
    return outline

WorkflowEngine._generate_outline = _generate_outline


class Orchestrator:
    def __init__(self):
        self.agent_registry = AgentRegistry()
        self.workflow_engine = WorkflowEngine(self.agent_registry)
        self._projects: Dict[str, Project] = {}
        self._event_history: List[WorkflowEvent] = []
    
    async def create_project(self, title: str, query: str, description: str = "") -> Project:
        project = Project(
            title=title,
            query=query,
            description=description
        )
        self._projects[project.id] = project
        await self._emit_event(project.id, AgentType.RESEARCH, "project_created", f"Project '{title}' created")
        return project
    
    async def execute_workflow(self, project_id: str) -> Project:
        project = self._projects.get(project_id)
        if not project:
            raise ValueError(f"Project not found: {project_id}")
        
        await self.execute_research_phase(project)
        await self.execute_writing_phase(project)
        
        project.updated_at = datetime.now()
        return project
    
    async def execute_research_phase(self, project: Project) -> ResearchTask:
        return await self.workflow_engine.execute_research_phase(project)
    
    async def execute_writing_phase(self, project: Project) -> List[WritingTask]:
        return await self.workflow_engine.execute_writing_phase(project)
    
    def get_project(self, project_id: str) -> Optional[Project]:
        return self._projects.get(project_id)
    
    def list_projects(self) -> List[Project]:
        return list(self._projects.values())
    
    async def _emit_event(self, project_id: str, agent_type: AgentType, event_type: str, message: str, data: dict = None):
        event = WorkflowEvent(
            project_id=project_id,
            agent_type=agent_type,
            event_type=event_type,
            message=message,
            data=data
        )
        self._event_history.append(event)
        logger.info(f"Event: {agent_type.value}/{event_type} - {message}")
    
    def get_events(self, project_id: Optional[str] = None) -> List[WorkflowEvent]:
        if project_id:
            return [e for e in self._event_history if e.project_id == project_id]
        return self._event_history
