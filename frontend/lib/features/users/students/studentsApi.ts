import { createApi, fetchBaseQuery } from "@reduxjs/toolkit/query/react";
import type { RootState } from "@/lib/store";
import type {
  StudentProfile,
  CreateStudentRequest,
  CreateStudentResponse,
  UpdateStudentRequest,
  PaginatedStudentsResponse,
  ListStudentsParams,
  MessageResponse,
} from "./types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:2385";

export const studentsApi = createApi({
  reducerPath: "studentsApi",
  baseQuery: fetchBaseQuery({
    baseUrl: `${API_BASE}/api/v1/users/students`,
    prepareHeaders: (headers, { getState }) => {
      const token = (getState() as RootState).auth.token;
      if (token) headers.set("authorization", `Bearer ${token}`);
      return headers;
    },
  }),
  tagTypes: ["Student"],
  endpoints: (builder) => ({
    // GET /students?skip=&limit=&search=
    listStudents: builder.query<PaginatedStudentsResponse, ListStudentsParams>({
      query: ({ skip, limit, search }) => {
        let url = `?skip=${skip}&limit=${limit}`;
        if (search) url += `&search=${encodeURIComponent(search)}`;
        return url;
      },
      providesTags: (result) =>
        result
          ? [
              ...result.items.map(({ siswa_id }) => ({
                type: "Student" as const,
                id: siswa_id,
              })),
              { type: "Student", id: "LIST" },
            ]
          : [{ type: "Student", id: "LIST" }],
    }),

    // GET /students/:siswaId
    getStudent: builder.query<StudentProfile, string>({
      query: (siswaId) => `/${siswaId}`,
      providesTags: (_result, _err, siswaId) => [{ type: "Student", id: siswaId }],
    }),

    // POST /students
    createStudent: builder.mutation<CreateStudentResponse, CreateStudentRequest>({
      query: (body) => ({ url: "", method: "POST", body }),
      invalidatesTags: [{ type: "Student", id: "LIST" }],
    }),

    // PATCH /students/:siswaId
    updateStudent: builder.mutation<
      StudentProfile,
      { siswaId: string; body: UpdateStudentRequest }
    >({
      query: ({ siswaId, body }) => ({
        url: `/${siswaId}`,
        method: "PATCH",
        body,
      }),
      invalidatesTags: (_result, _err, { siswaId }) => [
        { type: "Student", id: siswaId },
        { type: "Student", id: "LIST" },
      ],
    }),

    // DELETE /students/:siswaId
    deleteStudent: builder.mutation<MessageResponse, string>({
      query: (siswaId) => ({ url: `/${siswaId}`, method: "DELETE" }),
      invalidatesTags: (_result, _err, siswaId) => [
        { type: "Student", id: siswaId },
        { type: "Student", id: "LIST" },
      ],
    }),
  }),
});

export const {
  useListStudentsQuery,
  useGetStudentQuery,
  useCreateStudentMutation,
  useUpdateStudentMutation,
  useDeleteStudentMutation,
} = studentsApi;
