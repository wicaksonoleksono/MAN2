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
import { useCreateStudentMutation } from "@/lib/features/users/students/studentsApi";
import type { CreateStudentRequest } from "@/lib/features/users/students/types";
import type { JenisKelamin } from "@/lib/features/users/enums";
import { CredentialsDialog } from "./credentials-dialog";

const INITIAL_STATE: CreateStudentRequest = {
  nis: "",
  nama_lengkap: "",
  dob: "",
  tempat_lahir: "",
  jenis_kelamin: "Laki-Laki",
  alamat: "",
  nama_wali: "",
  nik: "",
  kelas_jurusan: "",
  tahun_masuk: new Date().getFullYear(),
  kontak: "",
  kewarganegaraan: "Indonesia",
};

export function StudentForm() {
  const [form, setForm] = useState<CreateStudentRequest>({ ...INITIAL_STATE });
  const [createStudent, { isLoading, error, reset }] = useCreateStudentMutation();
  const [credentials, setCredentials] = useState<{
    username: string;
    password: string;
  } | null>(null);

  const handleChange = (field: keyof CreateStudentRequest, value: string | number) => {
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
    const result = await createStudent(payload);
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

  return (
    <>
      <form onSubmit={handleSubmit} className="space-y-6 rounded-lg border p-6">
        <h2 className="text-lg font-semibold">Tambah Siswa Baru</h2>

        <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
          <div className="grid gap-2">
            <Label htmlFor="nis">NIS</Label>
            <Input
              id="nis"
              required
              value={form.nis}
              onChange={(e) => handleChange("nis", e.target.value)}
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
            <Label htmlFor="nama_wali">Nama Wali</Label>
            <Input
              id="nama_wali"
              required
              value={form.nama_wali}
              onChange={(e) => handleChange("nama_wali", e.target.value)}
            />
          </div>

          <div className="grid gap-2">
            <Label htmlFor="kelas_jurusan">Kelas/Jurusan</Label>
            <Input
              id="kelas_jurusan"
              required
              value={form.kelas_jurusan}
              onChange={(e) => handleChange("kelas_jurusan", e.target.value)}
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
          {isLoading ? "Menyimpan..." : "Simpan Siswa"}
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
