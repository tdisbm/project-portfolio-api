import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';
import { map, catchError, of } from 'rxjs';
import { AuthService } from '../services/auth.service';

export const authGuard: CanActivateFn = () => {
  const auth = inject(AuthService);
  const router = inject(Router);

  if (!auth.isLoggedIn()) {
    return router.createUrlTree(['/login']);
  }

  if (auth.currentUser()) {
    return true;
  }

  // Token exists but user not loaded (e.g. page refresh) — validate with the server
  return auth.fetchCurrentUser().pipe(
    map(() => true),
    catchError(() => {
      localStorage.removeItem('auth_token');
      return of(router.createUrlTree(['/login']));
    })
  );
};
