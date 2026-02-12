"use client";

import { useState, FormEvent } from "react";
import { useRouter } from "next/navigation";
import { useLoginMutation, useSignupMutation, type UserType } from "@/lib/features/auth/authApi";
import { useAppDispatch } from "@/lib/hooks";
import { setCredentials } from "@/lib/features/auth/authSlice";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from "@/components/ui/dialog";

type Mode = "login" | "signup";

interface AuthModalProps {
  initialMode?: Mode;
}

export default function AuthModal({ initialMode = "login" }: AuthModalProps) {
  const [mode, setMode] = useState<Mode>(initialMode);

  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [userType, setUserType] = useState<UserType>("Siswa");
  const [error, setError] = useState("");
  const [signupSuccess, setSignupSuccess] = useState(false);

  const router = useRouter();
  const dispatch = useAppDispatch();
  const [login, { isLoading: loginLoading }] = useLoginMutation();
  const [signup, { isLoading: signupLoading }] = useSignupMutation();

  const isLoading = loginLoading || signupLoading;

  const switchMode = (next: Mode) => {
    setMode(next);
    setError("");
    setSignupSuccess(false);
    setUsername("");
    setPassword("");
    setUserType("Siswa");
  };

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setError("");

    if (mode === "login") {
      try {
        const result = await login({ username, password }).unwrap();
        dispatch(setCredentials({ token: result.access_token, user: result.user }));
        router.push("/");
      } catch (err: any) {
        setError(err.data?.detail || "Login gagal. Silakan coba lagi.");
      }
    } else {
      try {
        await signup({ username, password, user_type: userType }).unwrap();
        setSignupSuccess(true);
        setTimeout(() => switchMode("login"), 2000);
      } catch (err: any) {
        setError(err.data?.detail || "Pendaftaran gagal. Silakan coba lagi.");
      }
    }
  };

  return (
    <div className="min-h-screen bg-background">
      <Dialog
        open={true}
        onOpenChange={(isOpen) => {
          if (!isOpen) router.push("/");
        }}
      >
        <DialogContent
          onInteractOutside={(e) => e.preventDefault()}
          onEscapeKeyDown={(e) => e.preventDefault()}
        >
          <DialogHeader>
            <DialogTitle>
              {mode === "login" ? "Masuk" : "Daftar"}
            </DialogTitle>
            <DialogDescription>
              {mode === "login"
                ? "Masuk ke akun Simandaya Anda."
                : "Buat akun Simandaya baru."}
            </DialogDescription>
          </DialogHeader>

          <form className="space-y-4" onSubmit={handleSubmit}>
            {error && (
              <div className="rounded-md bg-destructive/10 border border-destructive/20 p-3">
                <p className="text-sm text-destructive">{error}</p>
              </div>
            )}
            {signupSuccess && (
              <div className="rounded-md bg-primary/10 border border-primary/20 p-3">
                <p className="text-sm text-primary font-medium">
                  Akun berhasil dibuat! Mengalihkan ke halaman masuk...
                </p>
              </div>
            )}

            <div className="space-y-1">
              <label htmlFor="username" className="text-sm font-medium">
                Username
              </label>
              <input
                id="username"
                name="username"
                type="text"
                autoComplete="username"
                required
                className="w-full px-3 py-2 rounded-md border border-input bg-background text-sm focus:outline-none focus:ring-2 focus:ring-ring"
                placeholder={mode === "signup" ? "contoh: ahmad_siswa" : "Username"}
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                disabled={isLoading || signupSuccess}
              />
              {mode === "signup" && (
                <p className="text-xs text-muted-foreground">
                  3–100 karakter, huruf kecil, angka, underscore saja
                </p>
              )}
            </div>

            <div className="space-y-1">
              <label htmlFor="password" className="text-sm font-medium">
                Password
              </label>
              <input
                id="password"
                name="password"
                type="password"
                autoComplete={mode === "login" ? "current-password" : "new-password"}
                required
                className="w-full px-3 py-2 rounded-md border border-input bg-background text-sm focus:outline-none focus:ring-2 focus:ring-ring"
                placeholder={mode === "signup" ? "Min 8 karakter, huruf besar, kecil, angka" : "Password"}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                disabled={isLoading || signupSuccess}
              />
            </div>

            {mode === "signup" && (
              <div className="space-y-1">
                <label htmlFor="user_type" className="text-sm font-medium">
                  Tipe pengguna
                </label>
                <select
                  id="user_type"
                  name="user_type"
                  value={userType}
                  onChange={(e) => setUserType(e.target.value as UserType)}
                  disabled={isLoading || signupSuccess}
                  className="w-full px-3 py-2 rounded-md border border-input bg-background text-sm focus:outline-none focus:ring-2 focus:ring-ring"
                >
                  <option value="Siswa">Siswa</option>
                  <option value="Guru">Guru</option>
                  <option value="Admin">Admin</option>
                </select>
              </div>
            )}

            <button
              type="submit"
              disabled={isLoading || signupSuccess}
              className="w-full py-2 px-4 rounded-md bg-primary text-primary-foreground text-sm font-medium hover:bg-primary/90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading
                ? "Memuat..."
                : mode === "login"
                ? "Masuk"
                : "Daftar"}
            </button>
          </form>

          <div className="text-center text-sm text-muted-foreground">
            {mode === "login" ? (
              <>
                Belum punya akun?{" "}
                <button
                  type="button"
                  onClick={() => switchMode("signup")}
                  className="text-primary font-medium hover:underline"
                >
                  Daftar
                </button>
              </>
            ) : (
              <>
                Sudah punya akun?{" "}
                <button
                  type="button"
                  onClick={() => switchMode("login")}
                  className="text-primary font-medium hover:underline"
                >
                  Masuk
                </button>
              </>
            )}
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
