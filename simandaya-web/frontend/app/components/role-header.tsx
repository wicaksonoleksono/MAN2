"use client";

import { useState, useEffect } from "react";
import { useAppSelector } from "@/store/hooks";
import AdminHeader from "./admin-header";
import PublicHeader from "./public-header";

export default function RoleHeader() {
  const [mounted, setMounted] = useState(false);
  const user = useAppSelector((s) => s.auth.user);

  useEffect(() => {
    setMounted(true);
  }, []);

  if (mounted && user?.user_type === "Admin") return <AdminHeader />;
  return <PublicHeader />;
}
