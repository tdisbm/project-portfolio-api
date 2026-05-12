export interface Project {
  id: number;
  name: string;
  description: string;
  technologies_used: string[];
  date_start: string;
  date_end: string | null;
  created_at: string;
  updated_at: string;
}

export interface ProjectListResponse {
  count: number;
  total_pages: number;
  page: number;
  page_size: number;
  results: Project[];
}

export interface ProjectPayload {
  name: string;
  description: string;
  technologies_used: string[];
  date_start: string;
  date_end: string | null;
}

export interface ProjectFilters {
  name?: string;
  description?: string;
  dateStartAfter?: string;
  dateEndBefore?: string;
  technologies?: string[];
  sortColumn?: 'name' | 'date_start' | 'date_end';
  sortDirection?: 'asc' | 'desc';
}
