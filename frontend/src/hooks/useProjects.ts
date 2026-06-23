import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '../utils/api';
import type { Project, CreateProjectRequest } from '../types';

export function useProjects() {
  return useQuery<Project[]>({
    queryKey: ['projects'],
    queryFn: () => api.projects.list(),
    refetchInterval: 5000,
  });
}

export function useProject(id: string | undefined) {
  return useQuery<Project>({
    queryKey: ['project', id],
    queryFn: () => api.projects.get(id!),
    enabled: !!id,
    refetchInterval: 2000,
  });
}

export function useProjectEvents(projectId: string | undefined) {
  return useQuery({
    queryKey: ['projectEvents', projectId],
    queryFn: () => api.projects.getEvents(projectId!),
    enabled: !!projectId,
    refetchInterval: 1000,
  });
}

export function useProjectSources(projectId: string | undefined) {
  return useQuery({
    queryKey: ['projectSources', projectId],
    queryFn: () => api.projects.getSources(projectId!),
    enabled: !!projectId,
  });
}

export function useCreateProject() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (data: CreateProjectRequest) => api.projects.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['projects'] });
    },
  });
}

export function useDeleteProject() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (id: string) => api.projects.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['projects'] });
    },
  });
}

export function useExecuteWorkflow() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (id: string) => api.projects.execute(id),
    onMutate: async (id) => {
      await queryClient.cancelQueries({ queryKey: ['project', id] });
      const previousProject = queryClient.getQueryData(['project', id]);
      return { previousProject };
    },
    onError: (err, id, context) => {
      if (context?.previousProject) {
        queryClient.setQueryData(['project', id], context.previousProject);
      }
    },
    onSettled: (data, error, id) => {
      queryClient.invalidateQueries({ queryKey: ['project', id] });
      queryClient.invalidateQueries({ queryKey: ['projects'] });
    },
  });
}

export function useUpdateSection() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ projectId, sectionId, data }: { 
      projectId: string; 
      sectionId: string; 
      data: { title?: string; content?: string } 
    }) => api.projects.updateSection(projectId, sectionId, data),
    onSuccess: (updatedSection, variables) => {
      queryClient.invalidateQueries({ queryKey: ['project', variables.projectId] });
    },
  });
}

export function useExportPdf() {
  return useMutation({
    mutationFn: (id: string) => api.projects.exportPdf(id),
  });
}
