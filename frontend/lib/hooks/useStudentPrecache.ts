"use client";

import { useEffect } from "react";
import { usePrefetch } from "@/lib/features/users/usersApi";

const CHUNK = 30;

/**
 * Precaches adjacent 30-item chunks into RTK Query state so pagination
 * feels instant. Given the current offset (skip), it prefetches:
 *  - Next chunk  (skip + CHUNK) if within total
 *  - Prev chunk  (skip - CHUNK) if >= 0
 *
 * If the remaining items in either direction are < CHUNK, it just
 * prefetches whatever is left.
 *
 * @param skip   Current query offset (not display page number)
 * @param total  Total records returned by the API
 */
export function useStudentPrecache(skip: number, total: number) {
  const prefetch = usePrefetch("listStudents");

  useEffect(() => {
    if (total === 0) return;

    const chunkIndex = Math.floor(skip / CHUNK);

    // ── Next chunk ────────────────────────────────────────────────────────────
    const nextSkip = (chunkIndex + 1) * CHUNK;
    if (nextSkip < total) {
      const remaining = total - nextSkip;
      prefetch({ skip: nextSkip, limit: Math.min(CHUNK, remaining) });
    }

    // ── Prev chunk ────────────────────────────────────────────────────────────
    const prevSkip = (chunkIndex - 1) * CHUNK;
    if (prevSkip >= 0) {
      const remaining = total - prevSkip;
      prefetch({ skip: prevSkip, limit: Math.min(CHUNK, remaining) });
    }
  }, [skip, total, prefetch]);
}
