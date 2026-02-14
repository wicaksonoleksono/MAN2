"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useAppSelector } from "@/lib/hooks";

export default function AdminLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const { isAuthenticated, user } = useAppSelector((state) => state.auth);
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  useEffect(() => {
    if (mounted && (!isAuthenticated || !user || user.user_type !== "Admin")) {
      router.replace("/");
    }
  }, [mounted, isAuthenticated, user, router]);

  // Avoid hydration mismatch — render nothing until client-side mount
  if (!mounted) {
    return null;
  }

  if (!isAuthenticated || !user || user.user_type !== "Admin") {
    return null;
  }

  return <>{children}</>;
}
