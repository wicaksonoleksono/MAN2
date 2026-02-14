"use client";

import { useState, FormEvent } from "react";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from "@/components/ui/dialog";
import { useDebounce } from "@/lib/hooks/useDebounce";
import {
  useLazySearchPendingStudentsQuery,
  useLazySearchPendingTeachersQuery,
  useClaimStudentMutation,
  useClaimTeacherMutation,
} from "@/lib/features/registration/registrationApi";
import type { PendingStudentDTO, PendingTeacherDTO } from "@/lib/features/registration/types";

type Role = "siswa" | "guru";
type Step = 1 | 2 | 3;

interface RegisterModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSwitchToLogin: () => void;
}

export default function RegisterModal({ open, onOpenChange, onSwitchToLogin }: RegisterModalProps) {
  const [step, setStep] = useState<Step>(1);
  const [role, setRole] = useState<Role | null>(null);

  const [searchInput, setSearchInput] = useState("");
  const debouncedSearch = useDebounce(searchInput, 300);
  const [selectedStudent, setSelectedStudent] = useState<PendingStudentDTO | null>(null);
  const [selectedTeacher, setSelectedTeacher] = useState<PendingTeacherDTO | null>(null);

  const [searchStudents, { data: studentResults, isFetching: studentsFetching }] =
    useLazySearchPendingStudentsQuery();
  const [searchTeachers, { data: teacherResults, isFetching: teachersFetching }] =
    useLazySearchPendingTeachersQuery();
  const [claimStudent, { isLoading: claimingStudent }] = useClaimStudentMutation();
  const [claimTeacher, { isLoading: claimingTeacher }] = useClaimTeacherMutation();

  const [formData, setFormData] = useState({
    username: "",
    password: "",
    confirmPassword: "",
    nis: "",
    nip: "",
    dob: "",
    tempat_lahir: "",
    alamat: "",
    nama_wali: "",
    nik: "",
    tahun_masuk: "",
    kontak: "",
    mata_pelajaran: "",
    pendidikan_terakhir: "",
  });

  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const resetAll = () => {
    setStep(1);
    setRole(null);
    setSearchInput("");
    setSelectedStudent(null);
    setSelectedTeacher(null);
    setFormData({
      username: "", password: "", confirmPassword: "",
      nis: "", nip: "", dob: "", tempat_lahir: "", alamat: "",
      nama_wali: "", nik: "", tahun_masuk: "", kontak: "",
      mata_pelajaran: "", pendidikan_terakhir: "",
    });
    setError("");
    setSuccess("");
  };

  const handleOpenChange = (isOpen: boolean) => {
    if (!isOpen) resetAll();
    onOpenChange(isOpen);
  };

  const handleSearchChange = (value: string) => {
    setSearchInput(value);
    if (value.trim().length >= 2) {
      if (role === "siswa") searchStudents(value.trim());
      else searchTeachers(value.trim());
    }
  };

  const handleRoleSelect = (r: Role) => {
    setRole(r);
    setStep(2);
    setSearchInput("");
    setSelectedStudent(null);
    setSelectedTeacher(null);
  };

  const updateField = (field: string, value: string) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError("");

    if (formData.password !== formData.confirmPassword) {
      setError("Password dan konfirmasi password tidak sama.");
      return;
    }
    if (formData.password.length < 6) {
      setError("Password minimal 6 karakter.");
      return;
    }

    try {
      if (role === "siswa" && selectedStudent) {
        const result = await claimStudent({
          siswa_id: selectedStudent.siswa_id,
          username: formData.username,
          password: formData.password,
          nis: formData.nis,
          dob: formData.dob,
          tempat_lahir: formData.tempat_lahir,
          alamat: formData.alamat,
          nama_wali: formData.nama_wali,
          nik: formData.nik,
          tahun_masuk: parseInt(formData.tahun_masuk),
        }).unwrap();
        setSuccess(result.message);
        setTimeout(() => {
          resetAll();
          onOpenChange(false);
          onSwitchToLogin();
        }, 2000);
      } else if (role === "guru" && selectedTeacher) {
        const result = await claimTeacher({
          guru_id: selectedTeacher.guru_id,
          username: formData.username,
          password: formData.password,
          nip: formData.nip,
          dob: formData.dob,
          tempat_lahir: formData.tempat_lahir,
          alamat: formData.alamat,
          nik: formData.nik,
          tahun_masuk: parseInt(formData.tahun_masuk),
          kontak: formData.kontak || undefined,
          mata_pelajaran: formData.mata_pelajaran || undefined,
          pendidikan_terakhir: formData.pendidikan_terakhir || undefined,
        }).unwrap();
        setSuccess(result.message);
        setTimeout(() => {
          resetAll();
          onOpenChange(false);
          onSwitchToLogin();
        }, 2000);
      }
    } catch (err: any) {
      setError(err.data?.detail || "Pendaftaran gagal. Silakan coba lagi.");
    }
  };

  const isFetching = studentsFetching || teachersFetching;
  const isClaiming = claimingStudent || claimingTeacher;

  const dialogTitle =
    step === 1 ? "Daftar Akun" : step === 2 ? "Cari Nama Anda" : "Lengkapi Pendaftaran";
  const dialogDesc =
    step === 1
      ? "Pilih jenis akun Anda."
      : step === 2
      ? "Ketik nama lengkap Anda untuk mencari data yang sudah didaftarkan admin."
      : "Isi data berikut untuk menyelesaikan pendaftaran.";

  const inputClass = "w-full px-3 py-2 rounded-md border border-input bg-background text-sm focus:outline-none focus:ring-2 focus:ring-ring";

  return (
    <Dialog open={open} onOpenChange={handleOpenChange}>
      <DialogContent
        className="max-h-[85vh] overflow-y-auto"
        onInteractOutside={(e: Event) => e.preventDefault()}
      >
        <DialogHeader>
          <DialogTitle>{dialogTitle}</DialogTitle>
          <DialogDescription>{dialogDesc}</DialogDescription>
        </DialogHeader>

        {/* Step indicator */}
        <div className="flex items-center justify-center gap-2">
          {[1, 2, 3].map((s) => (
            <div
              key={s}
              className={`w-7 h-7 rounded-full flex items-center justify-center text-xs font-medium ${
                s === step
                  ? "bg-primary text-primary-foreground"
                  : s < step
                  ? "bg-primary/20 text-primary"
                  : "bg-muted text-muted-foreground"
              }`}
            >
              {s}
            </div>
          ))}
        </div>

        {/* Step 1: Role Selection */}
        {step === 1 && (
          <div className="space-y-3">
            <div className="grid grid-cols-2 gap-3">
              <button
                type="button"
                onClick={() => handleRoleSelect("siswa")}
                className="rounded-lg border-2 border-input p-4 text-center hover:border-primary transition-colors"
              >
                <p className="font-semibold">Saya Siswa</p>
                <p className="text-xs text-muted-foreground mt-1">Daftar sebagai siswa</p>
              </button>
              <button
                type="button"
                onClick={() => handleRoleSelect("guru")}
                className="rounded-lg border-2 border-input p-4 text-center hover:border-primary transition-colors"
              >
                <p className="font-semibold">Saya Guru</p>
                <p className="text-xs text-muted-foreground mt-1">Daftar sebagai guru</p>
              </button>
            </div>
            <div className="text-center text-sm text-muted-foreground">
              Sudah punya akun?{" "}
              <button
                type="button"
                onClick={() => { onOpenChange(false); onSwitchToLogin(); }}
                className="text-primary font-medium hover:underline"
              >
                Masuk
              </button>
            </div>
          </div>
        )}

        {/* Step 2: Find Name */}
        {step === 2 && (
          <div className="space-y-3">
            <input
              type="text"
              placeholder="Ketik nama lengkap (minimal 2 karakter)..."
              value={searchInput}
              onChange={(e) => handleSearchChange(e.target.value)}
              className={inputClass}
              autoFocus
            />

            {isFetching && <p className="text-sm text-muted-foreground">Mencari...</p>}

            {role === "siswa" && debouncedSearch.length >= 2 && !isFetching && studentResults && (
              <div className="space-y-2 max-h-[40vh] overflow-y-auto">
                {studentResults.items.length === 0 ? (
                  <div className="text-center py-4">
                    <p className="text-sm text-muted-foreground">Nama tidak ditemukan.</p>
                    <p className="text-xs text-muted-foreground mt-1">
                      Hubungi admin jika nama Anda belum terdaftar.
                    </p>
                  </div>
                ) : (
                  studentResults.items.map((student) => (
                    <div key={student.siswa_id}
                      className="flex items-center justify-between p-3 rounded-md border hover:bg-accent transition-colors">
                      <div>
                        <p className="font-medium text-sm">{student.nama_lengkap}</p>
                        <p className="text-xs text-muted-foreground">
                          {student.kelas_jurusan} - {student.jenis_kelamin}
                        </p>
                      </div>
                      <Button size="sm" onClick={() => { setSelectedStudent(student); setStep(3); }}>
                        Ini Saya
                      </Button>
                    </div>
                  ))
                )}
              </div>
            )}

            {role === "guru" && debouncedSearch.length >= 2 && !isFetching && teacherResults && (
              <div className="space-y-2 max-h-[40vh] overflow-y-auto">
                {teacherResults.items.length === 0 ? (
                  <div className="text-center py-4">
                    <p className="text-sm text-muted-foreground">Nama tidak ditemukan.</p>
                    <p className="text-xs text-muted-foreground mt-1">
                      Hubungi admin jika nama Anda belum terdaftar.
                    </p>
                  </div>
                ) : (
                  teacherResults.items.map((teacher) => (
                    <div key={teacher.guru_id}
                      className="flex items-center justify-between p-3 rounded-md border hover:bg-accent transition-colors">
                      <div>
                        <p className="font-medium text-sm">{teacher.nama_lengkap}</p>
                        <p className="text-xs text-muted-foreground">{teacher.jenis_kelamin}</p>
                      </div>
                      <Button size="sm" onClick={() => { setSelectedTeacher(teacher); setStep(3); }}>
                        Ini Saya
                      </Button>
                    </div>
                  ))
                )}
              </div>
            )}

            <Button variant="outline" onClick={() => { setStep(1); setSearchInput(""); }} className="w-full">
              Kembali
            </Button>
          </div>
        )}

        {/* Step 3: Complete Registration */}
        {step === 3 && (
          <form className="space-y-4" onSubmit={handleSubmit}>
            {error && (
              <div className="rounded-md bg-destructive/10 border border-destructive/20 p-3">
                <p className="text-sm text-destructive">{error}</p>
              </div>
            )}
            {success && (
              <div className="rounded-md bg-primary/10 border border-primary/20 p-3">
                <p className="text-sm text-primary font-medium">{success}</p>
              </div>
            )}

            <div className="rounded-md bg-muted p-3 space-y-1">
              <p className="text-sm">
                <span className="font-medium">Nama:</span>{" "}
                {role === "siswa" ? selectedStudent?.nama_lengkap : selectedTeacher?.nama_lengkap}
              </p>
              {role === "siswa" && selectedStudent && (
                <p className="text-sm">
                  <span className="font-medium">Kelas:</span> {selectedStudent.kelas_jurusan}
                </p>
              )}
              <p className="text-sm">
                <span className="font-medium">Jenis Kelamin:</span>{" "}
                {role === "siswa" ? selectedStudent?.jenis_kelamin : selectedTeacher?.jenis_kelamin}
              </p>
            </div>

            <div className="space-y-3">
              <h3 className="text-sm font-semibold">Akun</h3>
              <div className="space-y-1">
                <label className="text-sm font-medium">Username</label>
                <input type="text" required minLength={3} value={formData.username}
                  onChange={(e) => updateField("username", e.target.value)}
                  className={inputClass} disabled={isClaiming || !!success} />
              </div>
              <div className="space-y-1">
                <label className="text-sm font-medium">Password</label>
                <input type="password" required minLength={6} value={formData.password}
                  onChange={(e) => updateField("password", e.target.value)}
                  className={inputClass} disabled={isClaiming || !!success} />
              </div>
              <div className="space-y-1">
                <label className="text-sm font-medium">Konfirmasi Password</label>
                <input type="password" required minLength={6} value={formData.confirmPassword}
                  onChange={(e) => updateField("confirmPassword", e.target.value)}
                  className={inputClass} disabled={isClaiming || !!success} />
              </div>
            </div>

            <div className="space-y-3">
              <h3 className="text-sm font-semibold">Data Diri</h3>

              {role === "siswa" ? (
                <>
                  <div className="space-y-1">
                    <label className="text-sm font-medium">NIS</label>
                    <input type="text" required value={formData.nis}
                      onChange={(e) => updateField("nis", e.target.value)}
                      className={inputClass} disabled={isClaiming || !!success} />
                  </div>
                  <div className="space-y-1">
                    <label className="text-sm font-medium">Nama Wali</label>
                    <input type="text" required value={formData.nama_wali}
                      onChange={(e) => updateField("nama_wali", e.target.value)}
                      className={inputClass} disabled={isClaiming || !!success} />
                  </div>
                </>
              ) : (
                <>
                  <div className="space-y-1">
                    <label className="text-sm font-medium">NIP</label>
                    <input type="text" required value={formData.nip}
                      onChange={(e) => updateField("nip", e.target.value)}
                      className={inputClass} disabled={isClaiming || !!success} />
                  </div>
                  <div className="space-y-1">
                    <label className="text-sm font-medium">Kontak</label>
                    <input type="text" value={formData.kontak}
                      onChange={(e) => updateField("kontak", e.target.value)}
                      className={inputClass} disabled={isClaiming || !!success} />
                  </div>
                  <div className="space-y-1">
                    <label className="text-sm font-medium">Mata Pelajaran</label>
                    <input type="text" value={formData.mata_pelajaran}
                      onChange={(e) => updateField("mata_pelajaran", e.target.value)}
                      className={inputClass} disabled={isClaiming || !!success} />
                  </div>
                  <div className="space-y-1">
                    <label className="text-sm font-medium">Pendidikan Terakhir</label>
                    <input type="text" value={formData.pendidikan_terakhir}
                      onChange={(e) => updateField("pendidikan_terakhir", e.target.value)}
                      className={inputClass} disabled={isClaiming || !!success} />
                  </div>
                </>
              )}

              <div className="space-y-1">
                <label className="text-sm font-medium">Tanggal Lahir</label>
                <input type="text" required placeholder="DD/MM/YYYY" value={formData.dob}
                  onChange={(e) => updateField("dob", e.target.value)}
                  className={inputClass} disabled={isClaiming || !!success} />
              </div>
              <div className="space-y-1">
                <label className="text-sm font-medium">Tempat Lahir</label>
                <input type="text" required value={formData.tempat_lahir}
                  onChange={(e) => updateField("tempat_lahir", e.target.value)}
                  className={inputClass} disabled={isClaiming || !!success} />
              </div>
              <div className="space-y-1">
                <label className="text-sm font-medium">Alamat</label>
                <input type="text" required value={formData.alamat}
                  onChange={(e) => updateField("alamat", e.target.value)}
                  className={inputClass} disabled={isClaiming || !!success} />
              </div>
              <div className="space-y-1">
                <label className="text-sm font-medium">NIK</label>
                <input type="text" required value={formData.nik}
                  onChange={(e) => updateField("nik", e.target.value)}
                  className={inputClass} disabled={isClaiming || !!success} />
              </div>
              <div className="space-y-1">
                <label className="text-sm font-medium">Tahun Masuk</label>
                <input type="number" required min={2000} max={2100} value={formData.tahun_masuk}
                  onChange={(e) => updateField("tahun_masuk", e.target.value)}
                  className={inputClass} disabled={isClaiming || !!success} />
              </div>
            </div>

            <div className="flex gap-2">
              <Button type="button" variant="outline"
                onClick={() => { setStep(2); setError(""); setSuccess(""); }}
                disabled={isClaiming || !!success} className="flex-1">
                Kembali
              </Button>
              <Button type="submit" disabled={isClaiming || !!success} className="flex-1">
                {isClaiming ? "Memproses..." : "Daftar"}
              </Button>
            </div>
          </form>
        )}
      </DialogContent>
    </Dialog>
  );
}
