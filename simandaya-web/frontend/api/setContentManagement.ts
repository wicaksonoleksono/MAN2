import { createApi, fetchBaseQuery } from "@reduxjs/toolkit/query/react";
import type {
  CarouselSlide,
  CreateSlideRequest,
  UpdateSlideRequest,
  UploadImageResponse,
} from "@/types/cms";

export const cmsApi = createApi({
  reducerPath: "cmsApi",
  baseQuery: fetchBaseQuery({ baseUrl: "/api/cms" }),
  tagTypes: ["Slide"],
  endpoints: (builder) => ({
    listSlides: builder.query<CarouselSlide[], void>({
      query: () => "/slides",
      providesTags: [{ type: "Slide", id: "LIST" }],
    }),
    createSlide: builder.mutation<CarouselSlide, CreateSlideRequest>({
      query: (body) => ({ url: "/slides", method: "POST", body }),
      invalidatesTags: [{ type: "Slide", id: "LIST" }],
    }),
    updateSlide: builder.mutation<
      CarouselSlide,
      { id: string; body: UpdateSlideRequest }
    >({
      query: ({ id, body }) => ({ url: `/slides/${id}`, method: "PUT", body }),
      invalidatesTags: [{ type: "Slide", id: "LIST" }],
    }),
    deleteSlide: builder.mutation<void, string>({
      query: (id) => ({ url: `/slides/${id}`, method: "DELETE" }),
      invalidatesTags: [{ type: "Slide", id: "LIST" }],
    }),
    uploadImage: builder.mutation<UploadImageResponse, FormData>({
      query: (formData) => ({ url: "/upload", method: "POST", body: formData }),
    }),
  }),
});

export const {
  useListSlidesQuery,
  useCreateSlideMutation,
  useUpdateSlideMutation,
  useDeleteSlideMutation,
  useUploadImageMutation,
} = cmsApi;
