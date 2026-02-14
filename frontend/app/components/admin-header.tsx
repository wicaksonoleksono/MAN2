"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import Image from "next/image";
import { useAppDispatch } from "@/lib/hooks";
import { logout } from "@/lib/features/auth/authSlice";
import { useLogoutMutation } from "@/lib/features/auth/authApi";
import {
  NavigationMenu,
  NavigationMenuContent,
  NavigationMenuItem,
  NavigationMenuLink,
  NavigationMenuList,
  NavigationMenuTrigger,
  navigationMenuTriggerStyle,
} from "@/components/ui/navigation-menu";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from "@/components/ui/dialog";

export default function AdminHeader() {
  const router = useRouter();
  const dispatch = useAppDispatch();
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
        {/* Left - logo + school name */}
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

        {/* Right - admin nav */}
        <div className="flex items-center gap-2">
          <NavigationMenu>
            <NavigationMenuList className="gap-1">
              {/* Beranda link */}
              <NavigationMenuItem>
                <NavigationMenuLink asChild className={navigationMenuTriggerStyle() + " text-[#F3F1EA] bg-transparent hover:bg-white/10"}>
                  <Link href="/">Beranda</Link>
                </NavigationMenuLink>
              </NavigationMenuItem>

              {/* Kesiswaan dropdown */}
              <NavigationMenuItem>
                <NavigationMenuTrigger className="text-[#F3F1EA] bg-transparent hover:bg-white/10 data-[state=open]:bg-white/10">
                  Kesiswaan
                </NavigationMenuTrigger>
                <NavigationMenuContent>
                  <ul className="w-[240px] p-2">
                    <li>
                      <NavigationMenuLink asChild>
                        <Link
                          href="/admin/kesiswaan/absensi"
                          className="block select-none rounded-md p-3 text-sm leading-none no-underline outline-none transition-colors hover:bg-accent hover:text-accent-foreground focus:bg-accent focus:text-accent-foreground"
                        >
                          Absensi Masuk Sekolah
                        </Link>
                      </NavigationMenuLink>
                    </li>
                    <li>
                      <NavigationMenuLink asChild>
                        <Link
                          href="/admin/kesiswaan/izin"
                          className="block select-none rounded-md p-3 text-sm leading-none no-underline outline-none transition-colors hover:bg-accent hover:text-accent-foreground focus:bg-accent focus:text-accent-foreground"
                        >
                          Izin Kesiswaan
                        </Link>
                      </NavigationMenuLink>
                    </li>
                  </ul>
                </NavigationMenuContent>
              </NavigationMenuItem>

              {/* Manajemen Data dropdown */}
              <NavigationMenuItem>
                <NavigationMenuTrigger className="text-[#F3F1EA] bg-transparent hover:bg-white/10 data-[state=open]:bg-white/10">
                  Manajemen Data
                </NavigationMenuTrigger>
                <NavigationMenuContent>
                  <ul className="w-[280px] p-2">
                    <li>
                      <NavigationMenuLink asChild>
                        <Link
                          href="/admin/manajemen/siswa"
                          className="block select-none rounded-md p-3 text-sm leading-none no-underline outline-none transition-colors hover:bg-accent hover:text-accent-foreground focus:bg-accent focus:text-accent-foreground"
                        >
                          Penambahan Data Siswa
                        </Link>
                      </NavigationMenuLink>
                    </li>
                    <li>
                      <NavigationMenuLink asChild>
                        <Link
                          href="/admin/manajemen/civitas"
                          className="block select-none rounded-md p-3 text-sm leading-none no-underline outline-none transition-colors hover:bg-accent hover:text-accent-foreground focus:bg-accent focus:text-accent-foreground"
                        >
                          Penambahan Data Civitas Akademik
                        </Link>
                      </NavigationMenuLink>
                    </li>
                    <li>
                      <NavigationMenuLink asChild>
                        <Link
                          href="/admin/manajemen/setting"
                          className="block select-none rounded-md p-3 text-sm leading-none no-underline outline-none transition-colors hover:bg-accent hover:text-accent-foreground focus:bg-accent focus:text-accent-foreground"
                        >
                          Setting
                        </Link>
                      </NavigationMenuLink>
                    </li>
                  </ul>
                </NavigationMenuContent>
              </NavigationMenuItem>
            </NavigationMenuList>
          </NavigationMenu>

          {/* Logout button */}
          <button
            onClick={() => setShowLogoutDialog(true)}
            className="text-[#8FC3DD] hover:text-[#F3F1EA] transition-colors text-sm px-4 py-2"
          >
            Keluar
          </button>
        </div>
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
