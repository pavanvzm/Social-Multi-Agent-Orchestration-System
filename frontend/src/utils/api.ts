import type { Project, CreateProjectRequest, WorkflowEvent, Source } from '../types';

const API_BASE = '/api';

class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
    this.name = 'ApiError';
  }
}

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: {
      'Content-Type': 'application/json',
    },
    ...options,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Request failed' }));
    throw new ApiError(response.status, error.detail || 'Request failed');
  }

  if (response.headers.get('content-type')?.includes('application/pdf')) {
    return response.blob() as unknown as T;
  }

  return response.json();
}

export const api = {
  health: () => request<{ status: string; agents: string[] }>('/health'),
  
  projects: {
    list: () => request<Project[]>('/projects'),
    
    get: (id: string) => request<Project>(`/projects/${id}`),
    
    create: (data: CreateProjectRequest) => 
      request<Project>('/projects', {
        method: 'POST',
        body: JSON.stringify(data),
      }),
    
    delete: (id: string) => 
      request<{ message: string }>(`/projects/${id}`, {
        method: 'DELETE',
      }),
    
    execute: (id: string) =>
      request<{ message: string; project_id: string; status: string }>(`/projects/${id}/execute`, {
        method: 'POST',
      }),
    
    executeResearch: (id: string) =>
      request<{ message: string; sources_count: number; gaps: string[] }>(`/projects/${id}/research`, {
        method: 'POST',
      }),
    
    executeWriting: (id: string) =>
      request<{ message: string; sections_completed: number }>(`/projects/${id}/write`, {
        method: 'POST',
      }),
    
    getEvents: (id: string) => request<WorkflowEvent[]>(`/projects/${id}/events`),
    
    getSources: (id: string) => request<{ sources: Source[]; message?: string }>(`/projects/${id}/sources`),
    
    updateSection: (projectId: string, sectionId: string, data: { title?: string; content?: string }) =>
      request<Project>(`/projects/${projectId}/sections/${sectionId}`, {
        method: 'PATCH',
        body: JSON.stringify(data),
      }),
    
    exportPdf: async (id: string): Promise<Blob> => {
      const response = await fetch(`${API_BASE}/projects/${id}/export/pdf`);
      if (!response.ok) {
        throw new ApiError(response.status, 'Failed to export PDF');
      }
      return response.blob();
    },
  },
};

export { ApiError };
