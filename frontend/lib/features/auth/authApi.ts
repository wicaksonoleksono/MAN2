import { createApi, fetchBaseQuery } from "@reduxjs/toolkit/query/react";
import type { RootState } from "@/lib/store";
import type { User } from "./authSlice";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:2385";

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

export const authApi = createApi({
  reducerPath: "authApi",
  baseQuery: fetchBaseQuery({
    baseUrl: `${API_BASE}/api/v1/auth`,
    prepareHeaders: (headers, { getState }) => {
      const token = (getState() as RootState).auth.token;
      if (token) {
        headers.set("authorization", `Bearer ${token}`);
      }
      return headers;
    },
  }),
  endpoints: (builder) => ({
    signup: builder.mutation<SignupResponse, SignupRequest>({
      query: (body) => ({
        url: "/signup",
        method: "POST",
        body,
      }),
    }),
    login: builder.mutation<TokenResponse, LoginRequest>({
      query: (body) => ({
        url: "/login",
        method: "POST",
        body,
      }),
    }),
    verify: builder.query<User, void>({
      query: () => "/verify",
    }),
    logout: builder.mutation<MessageResponse, void>({
      query: () => ({
        url: "/logout",
        method: "POST",
      }),
    }),
  }),
});

export const {
  useSignupMutation,
  useLoginMutation,
  useVerifyQuery,
  useLogoutMutation,
} = authApi;
