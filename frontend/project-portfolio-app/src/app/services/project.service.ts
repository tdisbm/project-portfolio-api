import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Project, ProjectFilters, ProjectListResponse, ProjectPayload } from '../models/project.model';
import { environment } from '../../environments/environment';

@Injectable({ providedIn: 'root' })
export class ProjectService {
  private http = inject(HttpClient);
  private base = `${environment.apiUrl}/projects`;

  getProjects(filters: ProjectFilters = {}, page = 1, pageSize = 10): Observable<ProjectListResponse> {
    let params = new HttpParams().set('page', page).set('page_size', pageSize);
    if (filters.name?.trim()) params = params.set('name', filters.name.trim());
    if (filters.description?.trim()) params = params.set('description', filters.description.trim());
    if (filters.dateStartAfter) params = params.set('date_start_after', filters.dateStartAfter);
    if (filters.dateEndBefore) params = params.set('date_end_before', filters.dateEndBefore);
    for (const tech of filters.technologies ?? []) {
      params = params.append('technology', tech);
    }
    const sortParamMap: Record<string, string> = {
      name: 'order_by_name',
      date_start: 'order_by_date_start',
      date_end: 'order_by_date_end',
    };
    if (filters.sortColumn && filters.sortDirection) {
      params = params.set(sortParamMap[filters.sortColumn], filters.sortDirection);
    }
    return this.http.get<ProjectListResponse>(`${this.base}/`, { params });
  }

  createProject(data: ProjectPayload): Observable<Project> {
    return this.http.post<Project>(`${this.base}/create/`, data);
  }

  updateProject(id: number, data: Partial<ProjectPayload>): Observable<Project> {
    return this.http.patch<Project>(`${this.base}/${id}/update/`, data);
  }

  deleteProject(id: number): Observable<void> {
    return this.http.delete<void>(`${this.base}/delete/${id}/`);
  }
}
