import { createApi, fetchBaseQuery } from "@reduxjs/toolkit/query/react";
import type { RootState } from "@/lib/store";
import type {
  GuruProfile,
  PreRegisterTeacherRequest,
  PreRegisterResponse,
  UpdateGuruRequest,
  PaginatedTeachersResponse,
  ListTeachersParams,
  MessageResponse,
} from "./types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:2385";

export const teachersApi = createApi({
  reducerPath: "teachersApi",
  baseQuery: fetchBaseQuery({
    baseUrl: `${API_BASE}/api/v1/users/teachers`,
    prepareHeaders: (headers, { getState }) => {
      const token = (getState() as RootState).auth.token;
      if (token) headers.set("authorization", `Bearer ${token}`);
      return headers;
    },
  }),
  tagTypes: ["Teacher"],
  endpoints: (builder) => ({
    // GET /teachers?skip=&limit=&search=
    listTeachers: builder.query<PaginatedTeachersResponse, ListTeachersParams>({
      query: ({ skip, limit, search }) => {
        let url = `?skip=${skip}&limit=${limit}`;
        if (search) url += `&search=${encodeURIComponent(search)}`;
        return url;
      },
      providesTags: (result) =>
        result
          ? [
              ...result.items.map(({ guru_id }) => ({
                type: "Teacher" as const,
                id: guru_id,
              })),
              { type: "Teacher", id: "LIST" },
            ]
          : [{ type: "Teacher", id: "LIST" }],
    }),

    // GET /teachers/:guruId
    getTeacher: builder.query<GuruProfile, string>({
      query: (guruId) => `/${guruId}`,
      providesTags: (_result, _err, guruId) => [{ type: "Teacher", id: guruId }],
    }),

    // POST /teachers/pre-register
    preRegisterTeacher: builder.mutation<PreRegisterResponse, PreRegisterTeacherRequest>({
      query: (body) => ({ url: "/pre-register", method: "POST", body }),
      invalidatesTags: [{ type: "Teacher", id: "LIST" }],
    }),

    // PATCH /teachers/:guruId
    updateTeacher: builder.mutation<
      GuruProfile,
      { guruId: string; body: UpdateGuruRequest }
    >({
      query: ({ guruId, body }) => ({
        url: `/${guruId}`,
        method: "PATCH",
        body,
      }),
      invalidatesTags: (_result, _err, { guruId }) => [
        { type: "Teacher", id: guruId },
        { type: "Teacher", id: "LIST" },
      ],
    }),

    // DELETE /teachers/:guruId
    deleteTeacher: builder.mutation<MessageResponse, string>({
      query: (guruId) => ({ url: `/${guruId}`, method: "DELETE" }),
      invalidatesTags: (_result, _err, guruId) => [
        { type: "Teacher", id: guruId },
        { type: "Teacher", id: "LIST" },
      ],
    }),
  }),
});

export const {
  useListTeachersQuery,
  useGetTeacherQuery,
  usePreRegisterTeacherMutation,
  useUpdateTeacherMutation,
  useDeleteTeacherMutation,
} = teachersApi;
