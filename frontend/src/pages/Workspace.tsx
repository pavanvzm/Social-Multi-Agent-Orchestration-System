import { useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { 
  ArrowLeft, Play, Download, Search, FileText, Edit3, Check, X, AlertCircle 
} from 'lucide-react';
import { useProject, useProjectEvents, useProjectSources, useExecuteWorkflow, useUpdateSection, useExportPdf } from '../hooks/useProjects';
import { format } from 'date-fns';

const statusLabels: Record<string, string> = {
  draft: 'Draft',
  researching: 'Researching',
  writing: 'Writing',
  reviewing: 'Reviewing',
  completed: 'Completed',
  failed: 'Failed',
};

export function Workspace() {
  const { id } = useParams<{ id: string }>();
  const { data: project, isLoading } = useProject(id);
  const { data: events } = useProjectEvents(id);
  const { data: sourcesData } = useProjectSources(id);
  const executeWorkflow = useExecuteWorkflow();
  const updateSection = useUpdateSection();
  const exportPdf = useExportPdf();
  
  const [editingSection, setEditingSection] = useState<string | null>(null);
  const [editContent, setEditContent] = useState('');
  const [activeTab, setActiveTab] = useState<'content' | 'sources' | 'events'>('content');

  if (isLoading || !project) {
    return (
      <div className="container">
        <div className="loading-spinner">
          <div className="spinner" />
        </div>
      </div>
    );
  }

  const handleStartWorkflow = () => {
    if (id) {
      executeWorkflow.mutate(id);
    }
  };

  const handleExportPdf = async () => {
    if (!id) return;
    try {
      const blob = await exportPdf.mutateAsync(id);
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${project.title.replace(/\s+/g, '_')}_report.pdf`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Failed to export PDF:', error);
    }
  };

  const handleEditSection = (sectionId: string, content: string) => {
    setEditingSection(sectionId);
    setEditContent(content);
  };

  const handleSaveSection = () => {
    if (!id || !editingSection) return;
    updateSection.mutate({
      projectId: id,
      sectionId: editingSection,
      data: { content: editContent }
    });
    setEditingSection(null);
  };

  const handleCancelEdit = () => {
    setEditingSection(null);
    setEditContent('');
  };

  const isWorkflowRunning = ['researching', 'writing', 'reviewing'].includes(project.status);

  return (
    <div className="container">
      <div className="page-header">
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <Link to="/" className="btn btn-secondary btn-sm">
            <ArrowLeft size={16} />
            Back
          </Link>
          <div>
            <h1 className="page-title">{project.title}</h1>
            <p className="page-subtitle">{project.query}</p>
          </div>
        </div>
        <div className="actions-bar">
          <span className={`status-badge status-${project.status}`}>
            {isWorkflowRunning && <span className="status-indicator" />}
            {statusLabels[project.status]}
          </span>
          
          {project.status === 'draft' && (
            <button 
              className="btn btn-primary"
              onClick={handleStartWorkflow}
              disabled={executeWorkflow.isPending}
            >
              <Play size={16} />
              {executeWorkflow.isPending ? 'Starting...' : 'Start Research'}
            </button>
          )}
          
          {project.status === 'completed' && (
            <button 
              className="btn btn-success"
              onClick={handleExportPdf}
              disabled={exportPdf.isPending}
            >
              <Download size={16} />
              {exportPdf.isPending ? 'Exporting...' : 'Export PDF'}
            </button>
          )}
        </div>
      </div>

      <div className="workspace">
        {/* Agent Activity Panel */}
        <div className="panel">
          <div className="panel-header">
            <span className="panel-title">Agent Activity</span>
          </div>
          <div className="panel-content">
            <div className={`agent-card ${project.status === 'researching' ? 'active' : ''}`}>
              <div className="agent-header">
                <div className="agent-icon research">
                  <Search size={18} />
                </div>
                <div>
                  <div className="agent-name">Research Agent</div>
                  <div className="agent-status">
                    {project.status === 'draft' && 'Pending'}
                    {project.status === 'researching' && 'Collecting sources...'}
                    {project.status === 'writing' && 'Completed'}
                    {project.status === 'completed' && 'Completed'}
                  </div>
                </div>
              </div>
              {project.status === 'researching' && (
                <div className="progress-bar">
                  <div className="progress-fill" style={{ width: '60%' }} />
                </div>
              )}
            </div>

            <div className={`agent-card ${project.status === 'writing' ? 'active' : ''}`}>
              <div className="agent-header">
                <div className="agent-icon writer">
                  <FileText size={18} />
                </div>
                <div>
                  <div className="agent-name">Writer Agent</div>
                  <div className="agent-status">
                    {['draft', 'researching'].includes(project.status) && 'Waiting'}
                    {project.status === 'writing' && 'Generating content...'}
                    {project.status === 'completed' && 'Completed'}
                  </div>
                </div>
              </div>
              {project.status === 'writing' && (
                <div className="progress-bar">
                  <div className="progress-fill" style={{ width: '40%' }} />
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Main Content Panel */}
        <div className="panel">
          <div className="panel-header">
            <div style={{ display: 'flex', gap: '8px' }}>
              <button
                className={`btn btn-sm ${activeTab === 'content' ? 'btn-primary' : 'btn-secondary'}`}
                onClick={() => setActiveTab('content')}
              >
                Content
              </button>
              <button
                className={`btn btn-sm ${activeTab === 'events' ? 'btn-primary' : 'btn-secondary'}`}
                onClick={() => setActiveTab('events')}
              >
                Activity Log
              </button>
            </div>
          </div>
          
          <div className="panel-content content-preview">
            {activeTab === 'content' && (
              <>
                {project.sections.length === 0 && (
                  <div className="empty-state" style={{ padding: '32px' }}>
                    <FileText size={48} style={{ marginBottom: '16px', opacity: 0.5 }} />
                    <h3 className="empty-state-title">No content yet</h3>
                    <p className="empty-state-text">
                      Start the research workflow to generate your report
                    </p>
                  </div>
                )}
                
                {project.sections.map((section) => (
                  <div key={section.id} className="section-block">
                    <div className="section-title">
                      {section.title}
                      {section.confidence_score > 0 && (
                        <span className="section-confidence">
                          {Math.round(section.confidence_score * 100)}% confidence
                        </span>
                      )}
                      {project.status === 'completed' && (
                        <button
                          className="btn btn-sm btn-secondary"
                          style={{ marginLeft: 'auto' }}
                          onClick={() => handleEditSection(section.id, section.content)}
                        >
                          <Edit3 size={14} />
                          Edit
                        </button>
                      )}
                    </div>
                    
                    {editingSection === section.id ? (
                      <div>
                        <textarea
                          className="edit-area"
                          value={editContent}
                          onChange={(e) => setEditContent(e.target.value)}
                          rows={12}
                        />
                        <div style={{ display: 'flex', gap: '8px', marginTop: '12px' }}>
                          <button className="btn btn-success btn-sm" onClick={handleSaveSection}>
                            <Check size={14} />
                            Save
                          </button>
                          <button className="btn btn-secondary btn-sm" onClick={handleCancelEdit}>
                            <X size={14} />
                            Cancel
                          </button>
                        </div>
                      </div>
                    ) : (
                      <div className="section-content">
                        {section.content || (
                          <span style={{ color: 'var(--text-muted)', fontStyle: 'italic' }}>
                            Content will be generated...
                          </span>
                        )}
                      </div>
                    )}
                  </div>
                ))}
              </>
            )}

            {activeTab === 'events' && (
              <div>
                {(!events || events.length === 0) && (
                  <div style={{ textAlign: 'center', padding: '32px', color: 'var(--text-muted)' }}>
                    No activity yet
                  </div>
                )}
                {events?.map((event) => (
                  <div key={event.id} className="event-item">
                    <div className="event-time">
                      {format(new Date(event.timestamp), 'MMM d, HH:mm:ss')}
                      {' • '}
                      {event.agent_type}
                    </div>
                    <div className="event-message">
                      {event.event_type === 'failed' && (
                        <AlertCircle size={14} style={{ color: 'var(--error)', marginRight: '4px' }} />
                      )}
                      {event.message}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Sources Panel */}
        <div className="panel">
          <div className="panel-header">
            <span className="panel-title">Research Sources</span>
          </div>
          <div className="sources-panel">
            {(!sourcesData?.sources || sourcesData.sources.length === 0) && (
              <div style={{ textAlign: 'center', padding: '24px', color: 'var(--text-muted)' }}>
                Sources will appear after research
              </div>
            )}
            {sourcesData?.sources?.map((source) => (
              <div key={source.id} className="source-item">
                <div className="source-title">{source.title}</div>
                {source.url && (
                  <div className="source-url">{source.url}</div>
                )}
                <div className="source-score">
                  <span>Credibility</span>
                  <div className="score-bar">
                    <div 
                      className="score-fill" 
                      style={{ width: `${source.credibility_score * 100}%` }}
                    />
                  </div>
                  <span>{Math.round(source.credibility_score * 100)}%</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
