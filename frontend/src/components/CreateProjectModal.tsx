import { useState } from 'react';
import { X } from 'lucide-react';
import { useCreateProject } from '../hooks/useProjects';
import { useNavigate } from 'react-router-dom';

interface CreateProjectModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export function CreateProjectModal({ isOpen, onClose }: CreateProjectModalProps) {
  const [title, setTitle] = useState('');
  const [query, setQuery] = useState('');
  const [description, setDescription] = useState('');
  const createProject = useCreateProject();
  const navigate = useNavigate();

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const project = await createProject.mutateAsync({ title, query, description });
      onClose();
      navigate(`/project/${project.id}`);
    } catch (error) {
      console.error('Failed to create project:', error);
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2 className="modal-title">Create New Research Project</h2>
          <button className="modal-close" onClick={onClose}>
            <X size={20} />
          </button>
        </div>

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label className="form-label" htmlFor="title">
              Project Title
            </label>
            <input
              id="title"
              type="text"
              className="form-input"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="e.g., TechFlow Inc. Q4 2026 Market Analysis"
              required
            />
          </div>

          <div className="form-group">
            <label className="form-label" htmlFor="query">
              Research Query
            </label>
            <textarea
              id="query"
              className="form-textarea"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Describe what market research you need. Be specific about the company, time period, and focus areas."
              rows={4}
              required
            />
            <p className="form-hint">
              Include company name, time period, and specific areas of interest (e.g., "Market research for Tesla covering Q4 2026 performance, competitive landscape, and growth opportunities")
            </p>
          </div>

          <div className="form-group">
            <label className="form-label" htmlFor="description">
              Description (Optional)
            </label>
            <textarea
              id="description"
              className="form-textarea"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Additional notes or context about this research project..."
              rows={2}
            />
          </div>

          <div className="form-actions">
            <button type="button" className="btn btn-secondary" onClick={onClose}>
              Cancel
            </button>
            <button
              type="submit"
              className="btn btn-primary"
              disabled={createProject.isPending}
            >
              {createProject.isPending ? 'Creating...' : 'Create Project'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
