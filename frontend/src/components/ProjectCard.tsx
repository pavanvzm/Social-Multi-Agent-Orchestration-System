import { Link } from 'react-router-dom';
import { format } from 'date-fns';
import { FileText, Clock, Trash2 } from 'lucide-react';
import type { Project } from '../types';
import { useDeleteProject } from '../hooks/useProjects';
import clsx from 'clsx';

interface ProjectCardProps {
  project: Project;
}

const statusLabels: Record<string, string> = {
  draft: 'Draft',
  researching: 'Researching',
  writing: 'Writing',
  reviewing: 'Reviewing',
  completed: 'Completed',
  failed: 'Failed',
};

export function ProjectCard({ project }: ProjectCardProps) {
  const deleteProject = useDeleteProject();

  const handleDelete = (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (confirm('Are you sure you want to delete this project?')) {
      deleteProject.mutate(project.id);
    }
  };

  const statusClass = clsx('status-badge', `status-${project.status}`);

  return (
    <Link to={`/project/${project.id}`} style={{ textDecoration: 'none' }}>
      <div className="card project-card">
        <div className="project-header">
          <div>
            <h3 className="project-title">{project.title}</h3>
            <p className="project-query">{project.query}</p>
          </div>
          <span className={statusClass}>
            {['researching', 'writing', 'reviewing'].includes(project.status) && (
              <span className="status-indicator" />
            )}
            {statusLabels[project.status]}
          </span>
        </div>
        
        <div className="project-meta">
          <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
            <FileText size={14} />
            {project.sections.length} sections
          </span>
          <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
            <Clock size={14} />
            {format(new Date(project.updated_at), 'MMM d, yyyy')}
          </span>
          <button
            onClick={handleDelete}
            className="btn btn-sm"
            style={{ marginLeft: 'auto', background: 'transparent', padding: '4px' }}
            title="Delete project"
          >
            <Trash2 size={16} color="#EF4444" />
          </button>
        </div>
      </div>
    </Link>
  );
}
