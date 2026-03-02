"use client";

import { useState } from "react";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import type { CarouselSlide, CreateSlideRequest } from "@/types/cms";
import { useUploadImageMutation } from "@/api/setContentManagement";

const BG_OPTIONS = [
  { label: "Primary", value: "bg-primary" },
  { label: "Secondary", value: "bg-secondary" },
  { label: "Accent", value: "bg-accent" },
  { label: "Muted", value: "bg-muted" },
  { label: "Destructive", value: "bg-destructive" },
  { label: "Card", value: "bg-card" },
];

const FG_OPTIONS = [
  { label: "Primary Foreground", value: "text-primary-foreground" },
  { label: "Secondary Foreground", value: "text-secondary-foreground" },
  { label: "Accent Foreground", value: "text-accent-foreground" },
  { label: "Muted Foreground", value: "text-muted-foreground" },
  { label: "Card Foreground", value: "text-card-foreground" },
];

interface Props {
  defaultValues?: Partial<CarouselSlide>;
  onSubmit: (data: CreateSlideRequest) => void;
  isLoading?: boolean;
}

export function SlideForm({ defaultValues, onSubmit, isLoading }: Props) {
  const [title, setTitle] = useState(defaultValues?.title ?? "");
  const [description, setDescription] = useState(defaultValues?.description ?? "");
  const [bg, setBg] = useState(defaultValues?.bg ?? "bg-primary");
  const [fg, setFg] = useState(defaultValues?.fg ?? "text-primary-foreground");
  const [imageUrl, setImageUrl] = useState(defaultValues?.image_url ?? "");
  const [linkUrl, setLinkUrl] = useState(defaultValues?.link_url ?? "");
  const [linkLabel, setLinkLabel] = useState(defaultValues?.link_label ?? "");

  const [uploadImage, { isLoading: uploading }] = useUploadImageMutation();

  async function handleFileChange(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;
    const fd = new FormData();
    fd.append("file", file);
    const result = await uploadImage(fd).unwrap();
    setImageUrl(result.url);
  }

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    onSubmit({
      title,
      description,
      bg,
      fg,
      image_url: imageUrl || null,
      link_url: linkUrl || null,
      link_label: linkLabel || null,
    });
  }

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-4">
      <div className="flex flex-col gap-1.5">
        <Label htmlFor="title">Judul *</Label>
        <Input
          id="title"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          placeholder="Selamat Datang di SIMANDAYA"
          required
        />
      </div>

      <div className="flex flex-col gap-1.5">
        <Label htmlFor="description">Deskripsi *</Label>
        <Input
          id="description"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          placeholder="Deskripsi singkat slide..."
          required
        />
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div className="flex flex-col gap-1.5">
          <Label>Background</Label>
          <Select value={bg} onValueChange={setBg}>
            <SelectTrigger>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {BG_OPTIONS.map((opt) => (
                <SelectItem key={opt.value} value={opt.value}>
                  {opt.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        <div className="flex flex-col gap-1.5">
          <Label>Warna Teks</Label>
          <Select value={fg} onValueChange={setFg}>
            <SelectTrigger>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {FG_OPTIONS.map((opt) => (
                <SelectItem key={opt.value} value={opt.value}>
                  {opt.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      </div>

      {/* Live preview */}
      <div className={`${bg} ${fg} rounded-md p-4 text-center`}>
        <p className="font-semibold text-sm">{title || "Judul Slide"}</p>
        <p className="text-xs opacity-80 mt-1">{description || "Deskripsi slide"}</p>
      </div>

      <div className="flex flex-col gap-1.5">
        <Label htmlFor="image">Gambar (Opsional)</Label>
        <Input
          id="image"
          type="file"
          accept="image/*"
          onChange={handleFileChange}
          disabled={uploading}
        />
        {imageUrl && (
          <p className="text-xs text-muted-foreground truncate">Tersimpan: {imageUrl}</p>
        )}
      </div>

      <div className="flex flex-col gap-1.5">
        <Label htmlFor="link_url">Link CTA (Opsional)</Label>
        <Input
          id="link_url"
          value={linkUrl}
          onChange={(e) => setLinkUrl(e.target.value)}
          placeholder="https://example.com atau /path"
        />
      </div>

      <div className="flex flex-col gap-1.5">
        <Label htmlFor="link_label">Label Tombol (Opsional)</Label>
        <Input
          id="link_label"
          value={linkLabel}
          onChange={(e) => setLinkLabel(e.target.value)}
          placeholder="Pelajari Lebih Lanjut"
        />
      </div>

      <Button type="submit" disabled={isLoading || uploading} className="mt-2">
        {isLoading ? "Menyimpan..." : "Simpan"}
      </Button>
    </form>
  );
}
