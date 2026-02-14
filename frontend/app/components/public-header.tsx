"use client";

import { useState, useEffect, FormEvent } from "react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import Image from "next/image";
import { publicNav } from "@/config/navigation";
import { useAppDispatch, useAppSelector } from "@/store/hooks";
import { logout, setCredentials } from "@/store/slices/auth";
import { useLogoutMutation, useLoginMutation } from "@/api/auth";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from "@/components/ui/dialog";
import RegisterModal from "./register-modal";

export default function PublicHeader() {
  const pathname = usePathname();
  const router = useRouter();
  const dispatch = useAppDispatch();
  const isAuthenticated = useAppSelector((state) => state.auth.isAuthenticated);
  const [mounted, setMounted] = useState(false);
  const [showLogoutDialog, setShowLogoutDialog] = useState(false);
  const [showLoginDialog, setShowLoginDialog] = useState(false);
  const [showRegisterDialog, setShowRegisterDialog] = useState(false);
  const [logoutApi] = useLogoutMutation();

  const [loginUsername, setLoginUsername] = useState("");
  const [loginPassword, setLoginPassword] = useState("");
  const [loginError, setLoginError] = useState("");
  const [login, { isLoading: loginLoading }] = useLoginMutation();

  useEffect(() => {
    setMounted(true);
  }, []);

  const handleLogout = async () => {
    try {
      await logoutApi().unwrap();
    } finally {
      dispatch(logout());
      setShowLogoutDialog(false);
      router.push("/");
    }
  };

  const handleLogin = async (e: FormEvent) => {
    e.preventDefault();
    setLoginError("");

    try {
      const result = await login({ username: loginUsername, password: loginPassword }).unwrap();
      dispatch(setCredentials({ token: result.access_token, user: result.user }));
      setShowLoginDialog(false);
      setLoginUsername("");
      setLoginPassword("");
    } catch (err: any) {
      setLoginError(err.data?.detail || "Login gagal. Silakan coba lagi.");
    }
  };

  const openLoginDialog = () => {
    setLoginUsername("");
    setLoginPassword("");
    setLoginError("");
    setShowLoginDialog(true);
  };

  const switchToRegister = () => {
    setShowLoginDialog(false);
    setShowRegisterDialog(true);
  };

  const switchToLogin = () => {
    setShowRegisterDialog(false);
    openLoginDialog();
  };

  return (
    <>
      <header className="bg-[#173B52] text-[#F3F1EA] px-8 py-4 flex items-center justify-between">
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

        <nav className="flex items-center gap-8 text-sm">
          {publicNav.map(({ label, href }) => (
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

          {mounted && isAuthenticated ? (
            <button
              onClick={() => setShowLogoutDialog(true)}
              className="text-[#8FC3DD] hover:text-[#F3F1EA] transition-colors"
            >
              Keluar
            </button>
          ) : (
            <button
              onClick={openLoginDialog}
              className="text-[#8FC3DD] hover:text-[#F3F1EA] transition-colors"
            >
              Masuk
            </button>
          )}
        </nav>
      </header>

      {/* Login dialog */}
      <Dialog open={showLoginDialog} onOpenChange={setShowLoginDialog}>
        <DialogContent
          onInteractOutside={(e: Event) => e.preventDefault()}
          onEscapeKeyDown={() => setShowLoginDialog(false)}
        >
          <DialogHeader>
            <DialogTitle>Masuk</DialogTitle>
            <DialogDescription>
              Masuk ke akun Simandaya Anda.
            </DialogDescription>
          </DialogHeader>

          <form className="space-y-4" onSubmit={handleLogin}>
            {loginError && (
              <div className="rounded-md bg-destructive/10 border border-destructive/20 p-3">
                <p className="text-sm text-destructive">{loginError}</p>
              </div>
            )}

            <div className="space-y-1">
              <label htmlFor="login-username" className="text-sm font-medium">
                Username
              </label>
              <input
                id="login-username"
                type="text"
                autoComplete="username"
                required
                className="w-full px-3 py-2 rounded-md border border-input bg-background text-sm focus:outline-none focus:ring-2 focus:ring-ring"
                placeholder="Username"
                value={loginUsername}
                onChange={(e) => setLoginUsername(e.target.value)}
                disabled={loginLoading}
              />
            </div>

            <div className="space-y-1">
              <label htmlFor="login-password" className="text-sm font-medium">
                Password
              </label>
              <input
                id="login-password"
                type="password"
                autoComplete="current-password"
                required
                className="w-full px-3 py-2 rounded-md border border-input bg-background text-sm focus:outline-none focus:ring-2 focus:ring-ring"
                placeholder="Password"
                value={loginPassword}
                onChange={(e) => setLoginPassword(e.target.value)}
                disabled={loginLoading}
              />
            </div>

            <button
              type="submit"
              disabled={loginLoading}
              className="w-full py-2 px-4 rounded-md bg-primary text-primary-foreground text-sm font-medium hover:bg-primary/90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loginLoading ? "Memuat..." : "Masuk"}
            </button>
          </form>

          <div className="text-center text-sm text-muted-foreground">
            Belum punya akun?{" "}
            <button
              type="button"
              onClick={switchToRegister}
              className="text-primary font-medium hover:underline"
            >
              Daftar
            </button>
          </div>
        </DialogContent>
      </Dialog>

      {/* Register dialog */}
      <RegisterModal
        open={showRegisterDialog}
        onOpenChange={setShowRegisterDialog}
        onSwitchToLogin={switchToLogin}
      />

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
