"use client";

import { type ColumnDef } from "@tanstack/react-table";
import { Badge } from "@/components/ui/badge";
import type { GuruProfile } from "@/lib/features/users/teachers/types";

export const teacherColumns: ColumnDef<GuruProfile>[] = [
  {
    accessorKey: "nip",
    header: "NIP",
  },
  {
    accessorKey: "nama_lengkap",
    header: "Nama",
  },
  {
    accessorKey: "structural_role",
    header: "Jabatan",
    cell: ({ row }) => {
      const role = row.getValue("structural_role") as string;
      const bidang = row.original.bidang_wakasek;
      return bidang ? `${role} - ${bidang}` : role;
    },
  },
  {
    accessorKey: "mata_pelajaran",
    header: "Mata Pelajaran",
    cell: ({ row }) => row.getValue("mata_pelajaran") || "-",
  },
  {
    accessorKey: "tahun_masuk",
    header: "Tahun Masuk",
  },
  {
    accessorKey: "status_guru",
    header: "Status",
    cell: ({ row }) => {
      const status = row.getValue("status_guru") as string;
      const variant = status === "Aktif" ? "default" : "destructive";
      return <Badge variant={variant}>{status}</Badge>;
    },
  },
  {
    accessorKey: "kontak",
    header: "Kontak",
  },
];
