import type { User } from "./authSlice";

export type UserType = "Siswa" | "Guru" | "Admin";

export interface SignupRequest {
  username: string;
  password: string;
  user_type: UserType;
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface SignupResponse {
  message: string;
  user: User;
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
