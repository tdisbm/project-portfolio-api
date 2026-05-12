import { Injectable, inject, signal } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';
import { Observable, tap } from 'rxjs';
import { LoginPayload, LoginResponse, RegisterPayload, User } from '../models/user.model';
import { environment } from '../../environments/environment';

const TOKEN_KEY = 'auth_token';

@Injectable({ providedIn: 'root' })
export class AuthService {
  private http = inject(HttpClient);
  private router = inject(Router);
  private base = `${environment.apiUrl}/auth`;

  currentUser = signal<User | null>(null);

  getToken(): string | null {
    return localStorage.getItem(TOKEN_KEY);
  }

  isLoggedIn(): boolean {
    return !!this.getToken();
  }

  register(payload: RegisterPayload): Observable<LoginResponse> {
    return this.http.post<LoginResponse>(`${this.base}/register/`, payload).pipe(
      tap(res => {
        localStorage.setItem(TOKEN_KEY, res.token);
        this.currentUser.set(res.user);
      })
    );
  }

  login(payload: LoginPayload): Observable<LoginResponse> {
    return this.http.post<LoginResponse>(`${this.base}/login/`, payload).pipe(
      tap(res => {
        localStorage.setItem(TOKEN_KEY, res.token);
        this.currentUser.set(res.user);
      })
    );
  }

  logout(): void {
    const token = this.getToken();
    if (token) {
      this.http.post(`${this.base}/logout/`, {}).subscribe();
    }
    localStorage.removeItem(TOKEN_KEY);
    this.currentUser.set(null);
    this.router.navigate(['/login']);
  }

  fetchCurrentUser(): Observable<User> {
    return this.http.get<User>(`${this.base}/me/`).pipe(
      tap(user => this.currentUser.set(user))
    );
  }
}
