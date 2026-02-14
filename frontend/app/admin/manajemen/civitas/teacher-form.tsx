"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { useCreateTeacherMutation } from "@/lib/features/users/teachers/teachersApi";
import type { CreateGuruRequest } from "@/lib/features/users/teachers/types";
import type {
  JenisKelamin,
  StructuralRole,
  BidangWakasek,
} from "@/lib/features/users/enums";
import { CredentialsDialog } from "./credentials-dialog";

const STRUCTURAL_ROLES: StructuralRole[] = [
  "Kepala Sekolah",
  "Wakasek",
  "Guru",
  "Wali Kelas",
  "Guru BK / Konselor",
  "Kepala Tata Usaha",
  "Staf Tata Usaha",
  "Pustakawan",
  "Laboran",
  "Petugas UKS",
];

const BIDANG_WAKASEK: BidangWakasek[] = [
  "Kurikulum",
  "Kesiswaan",
  "Sarana dan Prasarana",
  "Humas",
];

const INITIAL_STATE: CreateGuruRequest = {
  nip: "",
  nama_lengkap: "",
  dob: "",
  tempat_lahir: "",
  jenis_kelamin: "Laki-Laki",
  alamat: "",
  nik: "",
  tahun_masuk: new Date().getFullYear(),
  kontak: "",
  kewarganegaraan: "Indonesia",
  structural_role: "Guru",
  bidang_wakasek: null,
  mata_pelajaran: "",
  pendidikan_terakhir: "",
};

export function TeacherForm() {
  const [form, setForm] = useState<CreateGuruRequest>({ ...INITIAL_STATE });
  const [createTeacher, { isLoading, error, reset }] = useCreateTeacherMutation();
  const [credentials, setCredentials] = useState<{
    username: string;
    password: string;
  } | null>(null);

  const handleChange = (field: keyof CreateGuruRequest, value: string | number | null) => {
    setForm((prev) => ({ ...prev, [field]: value }));
  };

  const formatDateForApi = (isoDate: string): string => {
    const [year, month, day] = isoDate.split("-");
    return `${day}/${month}/${year}`;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    reset();
    const payload = { ...form, dob: formatDateForApi(form.dob) };
    const result = await createTeacher(payload);
    if ("data" in result && result.data) {
      setCredentials({
        username: result.data.username,
        password: result.data.generated_password,
      });
      setForm({ ...INITIAL_STATE });
    }
  };

  const errorMessage =
    error && "data" in error
      ? (error.data as { detail?: string })?.detail
      : undefined;

  const isWakasek = form.structural_role === "Wakasek";

  return (
    <>
      <form onSubmit={handleSubmit} className="space-y-6 rounded-lg border p-6">
        <h2 className="text-lg font-semibold">Tambah Civitas Akademik</h2>

        <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
          <div className="grid gap-2">
            <Label htmlFor="nip">NIP</Label>
            <Input
              id="nip"
              required
              value={form.nip}
              onChange={(e) => handleChange("nip", e.target.value)}
            />
          </div>

          <div className="grid gap-2">
            <Label htmlFor="nama_lengkap">Nama Lengkap</Label>
            <Input
              id="nama_lengkap"
              required
              value={form.nama_lengkap}
              onChange={(e) => handleChange("nama_lengkap", e.target.value)}
            />
          </div>

          <div className="grid gap-2">
            <Label htmlFor="nik">NIK</Label>
            <Input
              id="nik"
              required
              value={form.nik}
              onChange={(e) => handleChange("nik", e.target.value)}
            />
          </div>

          <div className="grid gap-2">
            <Label htmlFor="tempat_lahir">Tempat Lahir</Label>
            <Input
              id="tempat_lahir"
              required
              value={form.tempat_lahir}
              onChange={(e) => handleChange("tempat_lahir", e.target.value)}
            />
          </div>

          <div className="grid gap-2">
            <Label htmlFor="dob">Tanggal Lahir</Label>
            <Input
              id="dob"
              type="date"
              required
              value={form.dob}
              onChange={(e) => handleChange("dob", e.target.value)}
            />
          </div>

          <div className="grid gap-2">
            <Label>Jenis Kelamin</Label>
            <Select
              value={form.jenis_kelamin}
              onValueChange={(val) => handleChange("jenis_kelamin", val as JenisKelamin)}
            >
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="Laki-Laki">Laki-Laki</SelectItem>
                <SelectItem value="Perempuan">Perempuan</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div className="grid gap-2 md:col-span-2">
            <Label htmlFor="alamat">Alamat</Label>
            <Input
              id="alamat"
              required
              value={form.alamat}
              onChange={(e) => handleChange("alamat", e.target.value)}
            />
          </div>

          <div className="grid gap-2">
            <Label>Jabatan</Label>
            <Select
              value={form.structural_role}
              onValueChange={(val) => {
                handleChange("structural_role", val as StructuralRole);
                if (val !== "Wakasek") handleChange("bidang_wakasek", null);
              }}
            >
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {STRUCTURAL_ROLES.map((role) => (
                  <SelectItem key={role} value={role}>
                    {role}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {isWakasek && (
            <div className="grid gap-2">
              <Label>Bidang Wakasek</Label>
              <Select
                value={form.bidang_wakasek || ""}
                onValueChange={(val) => handleChange("bidang_wakasek", val as BidangWakasek)}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Pilih bidang" />
                </SelectTrigger>
                <SelectContent>
                  {BIDANG_WAKASEK.map((bidang) => (
                    <SelectItem key={bidang} value={bidang}>
                      {bidang}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          )}

          <div className="grid gap-2">
            <Label htmlFor="mata_pelajaran">Mata Pelajaran</Label>
            <Input
              id="mata_pelajaran"
              value={form.mata_pelajaran || ""}
              onChange={(e) => handleChange("mata_pelajaran", e.target.value)}
            />
          </div>

          <div className="grid gap-2">
            <Label htmlFor="pendidikan_terakhir">Pendidikan Terakhir</Label>
            <Input
              id="pendidikan_terakhir"
              value={form.pendidikan_terakhir || ""}
              onChange={(e) => handleChange("pendidikan_terakhir", e.target.value)}
            />
          </div>

          <div className="grid gap-2">
            <Label htmlFor="tahun_masuk">Tahun Masuk</Label>
            <Input
              id="tahun_masuk"
              type="number"
              required
              value={form.tahun_masuk}
              onChange={(e) => handleChange("tahun_masuk", parseInt(e.target.value))}
            />
          </div>

          <div className="grid gap-2">
            <Label htmlFor="kontak">Kontak</Label>
            <Input
              id="kontak"
              required
              value={form.kontak}
              onChange={(e) => handleChange("kontak", e.target.value)}
            />
          </div>

          <div className="grid gap-2">
            <Label htmlFor="kewarganegaraan">Kewarganegaraan</Label>
            <Input
              id="kewarganegaraan"
              value={form.kewarganegaraan}
              onChange={(e) => handleChange("kewarganegaraan", e.target.value)}
            />
          </div>
        </div>

        {errorMessage && <p className="text-sm text-destructive">{errorMessage}</p>}

        <Button type="submit" disabled={isLoading}>
          {isLoading ? "Menyimpan..." : "Simpan Civitas"}
        </Button>
      </form>

      {credentials && (
        <CredentialsDialog
          open={!!credentials}
          onClose={() => setCredentials(null)}
          username={credentials.username}
          password={credentials.password}
        />
      )}
    </>
  );
}
