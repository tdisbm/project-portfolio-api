import { Component, OnInit, OnDestroy, inject, signal } from '@angular/core';
import { RouterLink } from '@angular/router';
import { MatDialog } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { MatTableModule } from '@angular/material/table';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatChipInputEvent, MatChipsModule } from '@angular/material/chips';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatDatepickerInputEvent, MatDatepickerModule } from '@angular/material/datepicker';
import { MatPaginatorModule, PageEvent } from '@angular/material/paginator';
import { provideNativeDateAdapter } from '@angular/material/core';
import { COMMA, ENTER } from '@angular/cdk/keycodes';
import { BehaviorSubject, Subscription } from 'rxjs';
import { debounceTime, distinctUntilChanged, switchMap } from 'rxjs/operators';
import { ProjectService } from '../../../services/project.service';
import { Project, ProjectFilters } from '../../../models/project.model';
import { AuthService } from '../../../services/auth.service';
import { ProjectFormDialogComponent } from '../../../shared/project-form-dialog/project-form-dialog.component';
import { ConfirmDialogComponent } from '../../../shared/confirm-dialog/confirm-dialog.component';

@Component({
  selector: 'app-project-list',
  providers: [provideNativeDateAdapter()],
  imports: [
    RouterLink,
    MatTableModule,
    MatButtonModule,
    MatIconModule,
    MatInputModule,
    MatFormFieldModule,
    MatChipsModule,
    MatProgressSpinnerModule,
    MatTooltipModule,
    MatToolbarModule,
    MatDatepickerModule,
    MatPaginatorModule,
  ],
  templateUrl: './project-list.component.html',
  styleUrl: './project-list.component.scss',
})
export class ProjectListComponent implements OnInit, OnDestroy {
  private projectService = inject(ProjectService);
  private dialog = inject(MatDialog);
  private snackBar = inject(MatSnackBar);
  auth = inject(AuthService);

  projects = signal<Project[]>([]);
  totalCount = signal(0);
  currentPage = signal(0);
  pageSize = signal(10);
  loading = signal(false);
  displayedColumns = ['no', 'name', 'description', 'technologies_used', 'date_start', 'date_end', 'actions'];

  techFilters: string[] = [];
  separatorKeysCodes = [ENTER, COMMA];
  sortColumn: 'name' | 'date_start' | 'date_end' | null = null;
  sortDirection: 'asc' | 'desc' = 'asc';

  startAfter = signal<Date | null>(null);
  endBefore = signal<Date | null>(null);

  private filtersSubject = new BehaviorSubject<ProjectFilters>({});
  private subs = new Subscription();

  ngOnInit(): void {
    this.subs.add(
      this.filtersSubject.pipe(
        debounceTime(300),
        distinctUntilChanged((a, b) => JSON.stringify(a) === JSON.stringify(b)),
        switchMap(filters => {
          this.loading.set(true);
          return this.projectService.getProjects(filters, this.currentPage() + 1, this.pageSize());
        })
      ).subscribe({
        next: res => {
          this.projects.set(res.results);
          this.totalCount.set(res.count);
          this.loading.set(false);
        },
        error: () => {
          this.loading.set(false);
          this.snackBar.open('Failed to load projects', 'Close', { duration: 3000 });
        },
      })
    );
    this.filtersSubject.next({});
  }

  ngOnDestroy(): void {
    this.subs.unsubscribe();
  }

  loadProjects(): void {
    this.loading.set(true);
    this.projectService.getProjects(this.filtersSubject.getValue(), this.currentPage() + 1, this.pageSize()).subscribe({
      next: res => {
        this.projects.set(res.results);
        this.totalCount.set(res.count);
        this.loading.set(false);
      },
      error: () => {
        this.loading.set(false);
        this.snackBar.open('Failed to load projects', 'Close', { duration: 3000 });
      },
    });
  }

  onPage(event: PageEvent): void {
    this.currentPage.set(event.pageIndex);
    this.pageSize.set(event.pageSize);
    this.loadProjects();
  }

  private pushFilters(patch: Partial<ProjectFilters>): void {
    this.currentPage.set(0);
    this.filtersSubject.next({ ...this.filtersSubject.getValue(), ...patch });
  }

  onSort(column: 'name' | 'date_start' | 'date_end'): void {
    if (this.sortColumn === column) {
      if (this.sortDirection === 'asc') {
        this.sortDirection = 'desc';
      } else {
        this.sortColumn = null;
        this.pushFilters({ sortColumn: undefined, sortDirection: undefined });
        return;
      }
    } else {
      this.sortColumn = column;
      this.sortDirection = 'asc';
    }
    this.pushFilters({ sortColumn: this.sortColumn!, sortDirection: this.sortDirection });
  }

  getSortIcon(column: string): string {
    if (this.sortColumn !== column) return 'unfold_more';
    return this.sortDirection === 'asc' ? 'arrow_upward' : 'arrow_downward';
  }

  onNameFilter(value: string): void {
    this.pushFilters({ name: value });
  }

  onDescriptionFilter(value: string): void {
    this.pushFilters({ description: value });
  }

  onStartAfterChange(e: MatDatepickerInputEvent<Date>): void {
    this.startAfter.set(e.value ?? null);
    this.pushFilters({ dateStartAfter: this.fmt(e.value ?? null) ?? undefined });
  }

  clearStartAfter(): void {
    this.startAfter.set(null);
    this.pushFilters({ dateStartAfter: undefined });
  }

  onEndBeforeChange(e: MatDatepickerInputEvent<Date>): void {
    this.endBefore.set(e.value ?? null);
    this.pushFilters({ dateEndBefore: this.fmt(e.value ?? null) ?? undefined });
  }

  clearEndBefore(): void {
    this.endBefore.set(null);
    this.pushFilters({ dateEndBefore: undefined });
  }

  addTechFilterFromClick(tech: string): void {
    if (!this.techFilters.includes(tech)) {
      this.techFilters = [...this.techFilters, tech];
      this.pushFilters({ technologies: this.techFilters });
    }
  }

  addTechFilter(event: MatChipInputEvent): void {
    const value = (event.value || '').trim();
    if (value && !this.techFilters.includes(value)) {
      this.techFilters = [...this.techFilters, value];
      this.pushFilters({ technologies: this.techFilters });
    }
    event.chipInput!.clear();
  }

  removeTechFilter(tech: string): void {
    this.techFilters = this.techFilters.filter(t => t !== tech);
    this.pushFilters({ technologies: this.techFilters });
  }

  openCreateDialog(): void {
    this.dialog
      .open(ProjectFormDialogComponent, { width: '600px', data: null })
      .afterClosed()
      .subscribe(ok => { if (ok) this.loadProjects(); });
  }

  openEditDialog(project: Project): void {
    this.loading.set(true);
    this.projectService.getProject(project.id).subscribe({
      next: freshProject => {
        this.loading.set(false);
        this.dialog
          .open(ProjectFormDialogComponent, { width: '800px', data: freshProject })
          .afterClosed()
          .subscribe(ok => { if (ok) this.loadProjects(); });
      },
      error: () => {
        this.loading.set(false);
        this.snackBar.open('Failed to load project', 'Close', { duration: 3000 });
      },
    });
  }

  confirmDelete(project: Project): void {
    this.dialog
      .open(ConfirmDialogComponent, { data: { message: `Delete "${project.name}"?` } })
      .afterClosed()
      .subscribe(confirmed => {
        if (!confirmed) return;
        this.projectService.deleteProject(project.id).subscribe({
          next: () => {
            this.snackBar.open('Project deleted', 'Close', { duration: 3000 });
            this.loadProjects();
          },
          error: () => this.snackBar.open('Failed to delete', 'Close', { duration: 3000 }),
        });
      });
  }

  private fmt(d: Date | null): string | null {
    if (!d) return null;
    const y = d.getFullYear();
    const m = String(d.getMonth() + 1).padStart(2, '0');
    const day = String(d.getDate()).padStart(2, '0');
    return `${y}-${m}-${day}`;
  }
}
