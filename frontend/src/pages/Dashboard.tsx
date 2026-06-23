import { useState } from 'react';
import { Plus, FileSearch } from 'lucide-react';
import { useProjects } from '../hooks/useProjects';
import { ProjectCard } from '../components/ProjectCard';
import { CreateProjectModal } from '../components/CreateProjectModal';

export function Dashboard() {
  const [showCreateModal, setShowCreateModal] = useState(false);
  const { data: projects, isLoading, error } = useProjects();

  return (
    <div className="container">
      <div className="page-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h1 className="page-title">Market Research Projects</h1>
          <p className="page-subtitle">
            Generate comprehensive market research reports using AI agents
          </p>
        </div>
        <button className="btn btn-primary btn-lg" onClick={() => setShowCreateModal(true)}>
          <Plus size={20} />
          New Research
        </button>
      </div>

      {isLoading && (
        <div className="loading-spinner">
          <div className="spinner" />
        </div>
      )}

      {error && (
        <div className="card" style={{ textAlign: 'center', padding: '32px' }}>
          <p style={{ color: 'var(--error)' }}>Failed to load projects. Please try again.</p>
        </div>
      )}

      {!isLoading && !error && projects?.length === 0 && (
        <div className="empty-state">
          <FileSearch className="empty-state-icon" />
          <h2 className="empty-state-title">No projects yet</h2>
          <p className="empty-state-text">
            Create your first market research project to get started with AI-powered research
          </p>
          <button className="btn btn-primary" onClick={() => setShowCreateModal(true)}>
            <Plus size={18} />
            Create First Project
          </button>
        </div>
      )}

      {projects && projects.length > 0 && (
        <div className="projects-grid">
          {projects.map((project) => (
            <ProjectCard key={project.id} project={project} />
          ))}
        </div>
      )}

      <CreateProjectModal
        isOpen={showCreateModal}
        onClose={() => setShowCreateModal(false)}
      />
    </div>
  );
}
