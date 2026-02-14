import { createApi, fetchBaseQuery } from "@reduxjs/toolkit/query/react";
import type {
  PendingStudentSearchResponse,
  PendingTeacherSearchResponse,
  ClaimStudentRequest,
  ClaimTeacherRequest,
  ClaimResponse,
} from "./types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:2385";

export const registrationApi = createApi({
  reducerPath: "registrationApi",
  baseQuery: fetchBaseQuery({
    baseUrl: `${API_BASE}/api/v1/registration`,
  }),
  endpoints: (builder) => ({
    searchPendingStudents: builder.query<PendingStudentSearchResponse, string>({
      query: (name) => `/students/search?name=${encodeURIComponent(name)}`,
    }),
    searchPendingTeachers: builder.query<PendingTeacherSearchResponse, string>({
      query: (name) => `/teachers/search?name=${encodeURIComponent(name)}`,
    }),
    claimStudent: builder.mutation<ClaimResponse, ClaimStudentRequest>({
      query: (body) => ({
        url: "/students/claim",
        method: "POST",
        body,
      }),
    }),
    claimTeacher: builder.mutation<ClaimResponse, ClaimTeacherRequest>({
      query: (body) => ({
        url: "/teachers/claim",
        method: "POST",
        body,
      }),
    }),
  }),
});

export const {
  useLazySearchPendingStudentsQuery,
  useLazySearchPendingTeachersQuery,
  useClaimStudentMutation,
  useClaimTeacherMutation,
} = registrationApi;
