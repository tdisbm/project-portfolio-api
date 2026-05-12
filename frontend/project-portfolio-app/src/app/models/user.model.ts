export interface User {
  id: number;
  username: string;
}

export interface LoginPayload {
  username: string;
  password: string;
}

export interface RegisterPayload {
  username: string;
  password: string;
}

export interface LoginResponse {
  token: string;
  user: User;
}
