"use client";

import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { useDeleteStudentMutation } from "@/lib/features/users/students/studentsApi";
import type { StudentProfile } from "@/lib/features/users/students/types";

interface StudentDeleteDialogProps {
  student: StudentProfile | null;
  open: boolean;
  onClose: () => void;
}

export function StudentDeleteDialog({ student, open, onClose }: StudentDeleteDialogProps) {
  const [deleteStudent, { isLoading, error, reset }] = useDeleteStudentMutation();

  const handleDelete = async () => {
    if (!student) return;
    const result = await deleteStudent(student.siswa_id);
    if ("data" in result) onClose();
  };

  const handleClose = () => {
    reset();
    onClose();
  };

  const errorMessage =
    error && "data" in error
      ? (error.data as { detail?: string })?.detail
      : undefined;

  return (
    <Dialog open={open} onOpenChange={handleClose}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Hapus Siswa</DialogTitle>
          <DialogDescription>
            Apakah Anda yakin ingin menghapus siswa{" "}
            <strong>{student?.nama_lengkap}</strong> (NIS: {student?.nis})?
            Tindakan ini tidak dapat dibatalkan. Akun login siswa juga akan dihapus.
          </DialogDescription>
        </DialogHeader>
        {errorMessage && <p className="text-sm text-destructive">{errorMessage}</p>}
        <DialogFooter>
          <Button variant="outline" onClick={handleClose}>
            Batal
          </Button>
          <Button variant="destructive" onClick={handleDelete} disabled={isLoading}>
            {isLoading ? "Menghapus..." : "Hapus"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
