import { createApi, fetchBaseQuery } from "@reduxjs/toolkit/query/react";
import type { RootState } from "@/lib/store";
import type { User } from "./authSlice";
import type {
  UserType,
  SignupRequest,
  LoginRequest,
  SignupResponse,
  TokenResponse,
  MessageResponse,
} from "./types";

export type { UserType, SignupRequest, LoginRequest, SignupResponse, TokenResponse, MessageResponse };

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:2385";

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
