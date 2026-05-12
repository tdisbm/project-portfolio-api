import { Component, inject, OnInit } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatChipInputEvent, MatChipsModule } from '@angular/material/chips';
import { provideNativeDateAdapter } from '@angular/material/core';
import { MatDatepickerModule } from '@angular/material/datepicker';
import { MAT_DIALOG_DATA, MatDialogModule, MatDialogRef } from '@angular/material/dialog';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
import { MatSnackBar } from '@angular/material/snack-bar';
import { COMMA, ENTER } from '@angular/cdk/keycodes';
import { Project, ProjectPayload } from '../../models/project.model';
import { ProjectService } from '../../services/project.service';

@Component({
  selector: 'app-project-form-dialog',
  providers: [provideNativeDateAdapter()],
  imports: [
    ReactiveFormsModule,
    MatDialogModule,
    MatFormFieldModule,
    MatInputModule,
    MatButtonModule,
    MatChipsModule,
    MatIconModule,
    MatDatepickerModule,
  ],
  templateUrl: './project-form-dialog.component.html',
  styleUrl: './project-form-dialog.component.scss',
})
export class ProjectFormDialogComponent implements OnInit {
  private fb = inject(FormBuilder);
  private projectService = inject(ProjectService);
  private snackBar = inject(MatSnackBar);
  private ref = inject(MatDialogRef<ProjectFormDialogComponent>);
  data = inject<Project | null>(MAT_DIALOG_DATA);

  isEdit = !!this.data;
  technologies: string[] = [];
  separatorKeysCodes = [ENTER, COMMA];
  saving = false;

  form = this.fb.group({
    name: ['', [Validators.required, Validators.maxLength(200)]],
    description: [''],
    date_start: this.fb.control<Date | null>(null, Validators.required),
    date_end: this.fb.control<Date | null>(null),
  });

  ngOnInit(): void {
    if (this.data) {
      this.form.patchValue({
        name: this.data.name,
        description: this.data.description,
        date_start: this.parseDate(this.data.date_start),
        date_end: this.data.date_end ? this.parseDate(this.data.date_end) : null,
      });
      this.technologies = [...this.data.technologies_used];
    }
  }

  addTech(event: MatChipInputEvent): void {
    const value = (event.value || '').trim();
    if (value && !this.technologies.includes(value)) {
      this.technologies.push(value);
    }
    event.chipInput!.clear();
  }

  removeTech(tech: string): void {
    this.technologies = this.technologies.filter(t => t !== tech);
  }

  save(): void {
    if (this.form.invalid) return;
    const v = this.form.getRawValue();
    const payload: ProjectPayload = {
      name: v.name!,
      description: v.description || '',
      technologies_used: this.technologies,
      date_start: this.toDateString(v.date_start)!,
      date_end: this.toDateString(v.date_end),
    };

    this.saving = true;
    const req$ = this.isEdit
      ? this.projectService.updateProject(this.data!.id, payload)
      : this.projectService.createProject(payload);

    req$.subscribe({
      next: () => {
        this.snackBar.open(
          this.isEdit ? 'Project updated' : 'Project created',
          'Close',
          { duration: 3000 }
        );
        this.ref.close(true);
      },
      error: () => {
        this.saving = false;
        this.snackBar.open('Failed to save project', 'Close', { duration: 3000 });
      },
    });
  }

  cancel(): void {
    this.ref.close(false);
  }

  private parseDate(s: string): Date {
    const [y, m, d] = s.split('-').map(Number);
    return new Date(y, m - 1, d);
  }

  private toDateString(d: Date | null): string | null {
    if (!d) return null;
    const y = d.getFullYear();
    const m = String(d.getMonth() + 1).padStart(2, '0');
    const day = String(d.getDate()).padStart(2, '0');
    return `${y}-${m}-${day}`;
  }
}
