import { createApi, fetchBaseQuery } from "@reduxjs/toolkit/query/react";
import type { RootState } from "@/lib/store";
import type {
  StudentProfile,
  CreateStudentRequest,
  CreateStudentResponse,
  UpdateStudentRequest,
  GuruProfile,
  CreateGuruRequest,
  CreateGuruResponse,
  UpdateGuruRequest,
  MessageResponse,
  PaginatedStudentsResponse,
  ListStudentsParams,
} from "./types";

export type {
  JenisKelamin,
  StatusSiswa,
  StatusGuru,
  StructuralRole,
  BidangWakasek,
  StudentProfile,
  CreateStudentRequest,
  CreateStudentResponse,
  UpdateStudentRequest,
  GuruProfile,
  CreateGuruRequest,
  CreateGuruResponse,
  UpdateGuruRequest,
  MessageResponse,
  PaginatedStudentsResponse,
  ListStudentsParams,
} from "./types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:2385";

export const usersApi = createApi({
  reducerPath: "usersApi",
  baseQuery: fetchBaseQuery({
    baseUrl: `${API_BASE}/api/v1/users`,
    prepareHeaders: (headers, { getState }) => {
      const token = (getState() as RootState).auth.token;
      if (token) headers.set("authorization", `Bearer ${token}`);
      return headers;
    },
  }),
  tagTypes: ["Student", "Teacher"],
  endpoints: (builder) => ({
    // ── Students ──────────────────────────────────────────────────────────────
    listStudents: builder.query<PaginatedStudentsResponse, ListStudentsParams>({
      query: ({ skip, limit }) => `/students?skip=${skip}&limit=${limit}`,
      providesTags: (result) =>
        result
          ? [
              ...result.items.map(({ siswa_id }) => ({ type: "Student" as const, id: siswa_id })),
              { type: "Student", id: "LIST" },
            ]
          : [{ type: "Student", id: "LIST" }],
    }),

    getStudent: builder.query<StudentProfile, string>({
      query: (siswaId) => `/students/${siswaId}`,
      providesTags: (_result, _err, siswaId) => [{ type: "Student", id: siswaId }],
    }),

    createStudent: builder.mutation<CreateStudentResponse, CreateStudentRequest>({
      query: (body) => ({ url: "/students", method: "POST", body }),
      invalidatesTags: [{ type: "Student", id: "LIST" }],
    }),

    updateStudent: builder.mutation<StudentProfile, { siswaId: string; body: UpdateStudentRequest }>({
      query: ({ siswaId, body }) => ({ url: `/students/${siswaId}`, method: "PATCH", body }),
      invalidatesTags: (_result, _err, { siswaId }) => [
        { type: "Student", id: siswaId },
        { type: "Student", id: "LIST" },
      ],
    }),

    deleteStudent: builder.mutation<MessageResponse, string>({
      query: (siswaId) => ({ url: `/students/${siswaId}`, method: "DELETE" }),
      invalidatesTags: (_result, _err, siswaId) => [
        { type: "Student", id: siswaId },
        { type: "Student", id: "LIST" },
      ],
    }),

    // ── Teachers ──────────────────────────────────────────────────────────────
    listTeachers: builder.query<GuruProfile[], void>({
      query: () => "/teachers",
      providesTags: (result) =>
        result
          ? [
              ...result.map(({ guru_id }) => ({ type: "Teacher" as const, id: guru_id })),
              { type: "Teacher", id: "LIST" },
            ]
          : [{ type: "Teacher", id: "LIST" }],
    }),

    getTeacher: builder.query<GuruProfile, string>({
      query: (guruId) => `/teachers/${guruId}`,
      providesTags: (_result, _err, guruId) => [{ type: "Teacher", id: guruId }],
    }),

    createTeacher: builder.mutation<CreateGuruResponse, CreateGuruRequest>({
      query: (body) => ({ url: "/teachers", method: "POST", body }),
      invalidatesTags: [{ type: "Teacher", id: "LIST" }],
    }),

    updateTeacher: builder.mutation<GuruProfile, { guruId: string; body: UpdateGuruRequest }>({
      query: ({ guruId, body }) => ({ url: `/teachers/${guruId}`, method: "PATCH", body }),
      invalidatesTags: (_result, _err, { guruId }) => [
        { type: "Teacher", id: guruId },
        { type: "Teacher", id: "LIST" },
      ],
    }),

    deleteTeacher: builder.mutation<MessageResponse, string>({
      query: (guruId) => ({ url: `/teachers/${guruId}`, method: "DELETE" }),
      invalidatesTags: (_result, _err, guruId) => [
        { type: "Teacher", id: guruId },
        { type: "Teacher", id: "LIST" },
      ],
    }),
  }),
});

export const {
  useListStudentsQuery,
  useGetStudentQuery,
  usePrefetch,
  useCreateStudentMutation,
  useUpdateStudentMutation,
  useDeleteStudentMutation,
  useListTeachersQuery,
  useGetTeacherQuery,
  useCreateTeacherMutation,
  useUpdateTeacherMutation,
  useDeleteTeacherMutation,
} = usersApi;
