export type AgentType = 'research' | 'writer' | 'planning' | 'reviewer';

export type TaskStatus = 'pending' | 'in_progress' | 'completed' | 'failed';

export type ProjectStatus = 'draft' | 'researching' | 'writing' | 'reviewing' | 'completed' | 'failed';

export interface Source {
  id: string;
  title: string;
  url?: string;
  credibility_score: number;
  content?: string;
  scraped_at: string;
}

export interface ReportSection {
  id: string;
  title: string;
  content: string;
  order: number;
  sources: string[];
  confidence_score: number;
  status: TaskStatus;
}

export interface ResearchTask {
  id: string;
  query: string;
  status: TaskStatus;
  sources: Source[];
  gaps: string[];
  started_at?: string;
  completed_at?: string;
  error?: string;
}

export interface WritingTask {
  id: string;
  section_id: string;
  research_task_id: string;
  status: TaskStatus;
  content: string;
  started_at?: string;
  completed_at?: string;
  error?: string;
}

export interface Project {
  id: string;
  title: string;
  description: string;
  query: string;
  status: ProjectStatus;
  sections: ReportSection[];
  research_task?: ResearchTask;
  writing_tasks: WritingTask[];
  created_at: string;
  updated_at: string;
  metadata?: Record<string, unknown>;
}

export interface WorkflowEvent {
  id: string;
  project_id: string;
  agent_type: AgentType;
  event_type: string;
  message: string;
  timestamp: string;
  data?: Record<string, unknown>;
}

export interface CreateProjectRequest {
  title: string;
  query: string;
  description?: string;
}
