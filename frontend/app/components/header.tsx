"use client";

import { useState } from "react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import Image from "next/image";
import { navRoutes } from "@/lib/routes";
import { useAppDispatch, useAppSelector } from "@/lib/hooks";
import { logout } from "@/lib/features/auth/authSlice";
import { useLogoutMutation } from "@/lib/features/auth/authApi";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from "@/components/ui/dialog";

export default function Header() {
  const pathname = usePathname();
  const router = useRouter();
  const dispatch = useAppDispatch();
  const isAuthenticated = useAppSelector((state) => state.auth.isAuthenticated);
  const [showLogoutDialog, setShowLogoutDialog] = useState(false);
  const [logoutApi] = useLogoutMutation();

  const handleLogout = async () => {
    try {
      await logoutApi().unwrap();
    } finally {
      dispatch(logout());
      setShowLogoutDialog(false);
      router.push("/");
    }
  };

  return (
    <>
      <header className="bg-[#173B52] text-[#F3F1EA] px-8 py-4 flex items-center justify-between">
        {/* Left — logo + school name */}
        <div className="flex items-center gap-4">
          <Image
            src="/man2.png"
            alt="Logo"
            width={60}
            height={60}
            priority
          />
          <div className="leading-tight">
            <h1 className="text-xl font-semibold tracking-wide">
              Madrasah Aliyah Negeri 2 Yogyakarta
            </h1>
            <p className="text-sm text-[#8FC3DD] italic">
              Ukir prasasti dengan prestasi
            </p>
          </div>
        </div>

        {/* Right — nav + auth */}
        <nav className="flex items-center gap-8 text-sm">
          {navRoutes.map(({ label, href }) => (
            <Link
              key={href}
              href={href}
              className={
                pathname === href
                  ? "font-semibold border-b-2 border-[#C8A24A] text-[#EAD79A] pb-1"
                  : "text-[#8FC3DD] hover:text-[#F3F1EA] transition-colors"
              }
            >
              {label}
            </Link>
          ))}

          {isAuthenticated ? (
            <button
              onClick={() => setShowLogoutDialog(true)}
              className="text-[#8FC3DD] hover:text-[#F3F1EA] transition-colors"
            >
              Keluar
            </button>
          ) : (
            <Link
              href="/login"
              className={
                pathname === "/login"
                  ? "font-semibold border-b-2 border-[#C8A24A] text-[#EAD79A] pb-1"
                  : "text-[#8FC3DD] hover:text-[#F3F1EA] transition-colors"
              }
            >
              Masuk
            </Link>
          )}
        </nav>
      </header>

      {/* Logout confirmation dialog */}
      <Dialog open={showLogoutDialog} onOpenChange={setShowLogoutDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Konfirmasi Keluar</DialogTitle>
            <DialogDescription>
              Apakah Anda ingin keluar dari Simandaya?
            </DialogDescription>
          </DialogHeader>
          <DialogFooter className="gap-2">
            <button
              onClick={() => setShowLogoutDialog(false)}
              className="px-4 py-2 rounded-md border border-input text-sm hover:bg-muted transition-colors"
            >
              Batal
            </button>
            <button
              onClick={handleLogout}
              className="px-4 py-2 rounded-md bg-primary text-primary-foreground text-sm font-medium hover:bg-primary/90 transition-colors"
            >
              Ya, Keluar
            </button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
}
