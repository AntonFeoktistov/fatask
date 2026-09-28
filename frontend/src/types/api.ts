
// --- Auth ---
export interface UserCreate {
  email: string;
  username: string;
  password: string;
}

export interface UserResponse {
  email: string;
  username: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type?: string; // "bearer" по умолчанию
  expires_in: number;
}

export interface RefreshTokenRequest {
  refresh_token: string;
}

// --- Tasks ---
export interface TaskCreate {
  title: string;
  description?: string;
}

export interface TaskUpdate {
  title?: string;
  description?: string;
  is_done?: boolean;
}

export interface TaskResponse {
  oid: string; // UUID приходит как строка
  title: string;
  description: string | null;
  is_done: boolean;
  created_at: string; // ISO 8601
  updated_at: string; // ISO 8601
}