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
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

interface CredentialsDialogProps {
  open: boolean;
  onClose: () => void;
  username: string;
  password: string;
}

export function CredentialsDialog({
  open,
  onClose,
  username,
  password,
}: CredentialsDialogProps) {
  const handleCopy = () => {
    const text = `Username: ${username}\nPassword: ${password}`;
    navigator.clipboard.writeText(text);
  };

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Akun Berhasil Dibuat</DialogTitle>
          <DialogDescription>
            Simpan kredensial berikut. Password tidak dapat dilihat kembali.
          </DialogDescription>
        </DialogHeader>
        <div className="grid gap-4 py-4">
          <div className="grid gap-2">
            <Label>Username</Label>
            <Input readOnly value={username} />
          </div>
          <div className="grid gap-2">
            <Label>Password</Label>
            <Input readOnly value={password} />
          </div>
        </div>
        <DialogFooter>
          <Button variant="outline" onClick={handleCopy}>
            Salin
          </Button>
          <Button onClick={onClose}>Tutup</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
