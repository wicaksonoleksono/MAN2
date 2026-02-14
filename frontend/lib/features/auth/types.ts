import type { User } from "./authSlice";

export type UserType = "Siswa" | "Guru" | "Admin";

export interface LoginRequest {
  username: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
  user: User;
}

export interface MessageResponse {
  message: string;
}
