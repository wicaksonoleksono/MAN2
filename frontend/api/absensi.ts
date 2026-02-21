import { createApi } from "@reduxjs/toolkit/query/react";
import { createBaseQuery } from "./base";

export interface PublicAbsensi {
  absensi_id: string;
  nama_siswa: string;
  kelas: string | null;
  tanggal: string;
  time_in: string | null;
  time_out: string | null;
  status: string;
}

export interface PublicIzinKeluar {
  izin_id: string;
  nama_siswa: string;
  kelas: string | null;
  created_at: string;
  keterangan: string;
  waktu_kembali: string | null;
}

interface ListParams {
  tanggal: string;
  search?: string;
  skip?: number;
  limit?: number;
}

export const absensiApi = createApi({
  reducerPath: "absensiApi",
  baseQuery: createBaseQuery("/absensi/public"),
  tagTypes: ["Absensi", "IzinKeluar"],
  endpoints: (builder) => ({
    listPublicAttendance: builder.query<PublicAbsensi[], ListParams>({
      query: ({ tanggal, search, skip = 0, limit = 50 }) => {
        let url = `/attendance?tanggal=${tanggal}&skip=${skip}&limit=${limit}`;
        if (search) url += `&search=${encodeURIComponent(search)}`;
        return url;
      },
      providesTags: (_r, _e, { tanggal }) => [
        { type: "Absensi", id: tanggal },
      ],
    }),
    listPublicIzinKeluar: builder.query<PublicIzinKeluar[], ListParams>({
      query: ({ tanggal, search, skip = 0, limit = 50 }) => {
        let url = `/izin-keluar?tanggal=${tanggal}&skip=${skip}&limit=${limit}`;
        if (search) url += `&search=${encodeURIComponent(search)}`;
        return url;
      },
      providesTags: (_r, _e, { tanggal }) => [
        { type: "IzinKeluar", id: tanggal },
      ],
    }),
  }),
});

export const {
  useListPublicAttendanceQuery,
  useListPublicIzinKeluarQuery,
} = absensiApi;
