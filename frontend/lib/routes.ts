export interface NavLink {
  label: string;
  href: string;
}

export interface NavDropdown {
  label: string;
  children: NavLink[];
  width?: string;
}

export type NavItem = NavLink | NavDropdown;

export function isDropdown(item: NavItem): item is NavDropdown {
  return "children" in item;
}

export const navRoutes: NavLink[] = [
  { label: "Beranda", href: "/" },
];

export const adminNavRoutes: NavItem[] = [
  { label: "Beranda", href: "/" },
  {
    label: "Kesiswaan",
    width: "w-[240px]",
    children: [
      { label: "Absensi Masuk Sekolah", href: "/admin/kesiswaan/absensi" },
      { label: "Izin Kesiswaan", href: "/admin/kesiswaan/izin" },
    ],
  },
  {
    label: "Manajemen Data",
    width: "w-[280px]",
    children: [
      { label: "Penambahan Data Siswa", href: "/admin/manajemen/siswa" },
      { label: "Penambahan Data Civitas Akademik", href: "/admin/manajemen/civitas" },
      { label: "Pengaturan Manajemen Konten", href: "/admin/manajemen/pengaturan-cms" },
    ],
  },
];
