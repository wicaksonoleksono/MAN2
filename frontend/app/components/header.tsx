"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { navRoutes } from "@/lib/routes";
import Image from "next/image";

export default function Header() {
  const pathname = usePathname();

  return (
    <header className="bg-[#173B52] text-[#F3F1EA] px-8 py-4 flex items-center justify-between">
      {/* Left Section */}
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

      {/* Navigation */}
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
      </nav>
    </header>
  );
}
