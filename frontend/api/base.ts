import { fetchBaseQuery } from "@reduxjs/toolkit/query/react";
import type { RootState } from "@/store";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:2385";

export function createBaseQuery(path: string) {
  return fetchBaseQuery({
    baseUrl: `${API_BASE}/api/v1${path}`,
    prepareHeaders: (headers, { getState }) => {
      const token = (getState() as RootState).auth.token;
      if (token) headers.set("authorization", `Bearer ${token}`);
      return headers;
    },
  });
}
