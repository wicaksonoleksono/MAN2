"use client";

import { useAppDispatch, useAppSelector } from "@/store/hooks";
import {
  openAddDialog,
  closeAddDialog,
  openEditDialog,
  closeEditDialog,
  openDeleteDialog,
  closeDeleteDialog,
} from "@/store/slices/cms";
import {
  useListSlidesQuery,
  useCreateSlideMutation,
  useUpdateSlideMutation,
  useDeleteSlideMutation,
} from "@/api/setContentManagement";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import { SlideForm } from "./slide-form";
import type { CreateSlideRequest } from "@/types/cms";
import { Pencil, Trash2, Plus, Eye, EyeOff } from "lucide-react";

export default function SettingPage() {
  const dispatch = useAppDispatch();
  const { isAddDialogOpen, isEditDialogOpen, isDeleteDialogOpen, selectedSlide } =
    useAppSelector((state) => state.cms);

  const { data: slides = [], isLoading } = useListSlidesQuery();
  const [createSlide, { isLoading: creating }] = useCreateSlideMutation();
  const [updateSlide, { isLoading: updating }] = useUpdateSlideMutation();
  const [deleteSlide, { isLoading: deleting }] = useDeleteSlideMutation();

  async function handleCreate(data: CreateSlideRequest) {
    await createSlide(data).unwrap();
    dispatch(closeAddDialog());
  }

  async function handleUpdate(data: CreateSlideRequest) {
    if (!selectedSlide) return;
    await updateSlide({ id: selectedSlide.id, body: data }).unwrap();
    dispatch(closeEditDialog());
  }

  async function handleDelete() {
    if (!selectedSlide) return;
    await deleteSlide(selectedSlide.id).unwrap();
    dispatch(closeDeleteDialog());
  }

  async function handleToggleActive(id: string, current: boolean) {
    await updateSlide({ id, body: { is_active: !current } }).unwrap();
  }

  return (
    <div className="p-8 max-w-4xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold">Pengaturan CMS</h1>
          <p className="mt-1 text-muted-foreground">
            Kelola slide carousel halaman utama
          </p>
        </div>
        <Button onClick={() => dispatch(openAddDialog())}>
          <Plus className="mr-2 h-4 w-4" />
          Tambah Slide
        </Button>
      </div>

      {isLoading && (
        <p className="text-center text-muted-foreground py-12">Memuat...</p>
      )}

      <div className="flex flex-col gap-3">
        {slides.map((slide) => (
          <Card key={slide.id}>
            <CardContent className="p-4 flex items-center gap-4">
              <div
                className={`${slide.bg} ${slide.fg} rounded-md w-24 h-16 flex items-center justify-center text-xs font-medium text-center p-1 shrink-0`}
              >
                {slide.title}
              </div>

              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-1">
                  <span className="font-medium truncate">{slide.title}</span>
                  <Badge variant={slide.is_active ? "default" : "secondary"}>
                    {slide.is_active ? "Aktif" : "Non-aktif"}
                  </Badge>
                </div>
                <p className="text-sm text-muted-foreground truncate">
                  {slide.description}
                </p>
                {slide.link_url && (
                  <p className="text-xs text-muted-foreground mt-0.5">
                    Link: {slide.link_url}
                  </p>
                )}
              </div>

              <div className="flex items-center gap-1 shrink-0">
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={() => handleToggleActive(slide.id, slide.is_active)}
                  title={slide.is_active ? "Nonaktifkan" : "Aktifkan"}
                >
                  {slide.is_active ? (
                    <Eye className="h-4 w-4" />
                  ) : (
                    <EyeOff className="h-4 w-4" />
                  )}
                </Button>
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={() => dispatch(openEditDialog(slide))}
                >
                  <Pencil className="h-4 w-4" />
                </Button>
                <Button
                  variant="ghost"
                  size="icon"
                  className="text-destructive hover:text-destructive"
                  onClick={() => dispatch(openDeleteDialog(slide))}
                >
                  <Trash2 className="h-4 w-4" />
                </Button>
              </div>
            </CardContent>
          </Card>
        ))}

        {!isLoading && slides.length === 0 && (
          <p className="text-center text-muted-foreground py-12">
            Belum ada slide. Klik &quot;Tambah Slide&quot; untuk memulai.
          </p>
        )}
      </div>

      {/* Add Dialog */}
      <Dialog
        open={isAddDialogOpen}
        onOpenChange={(open) => !open && dispatch(closeAddDialog())}
      >
        <DialogContent className="max-w-lg max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Tambah Slide Baru</DialogTitle>
            <DialogDescription>
              Isi detail slide yang akan ditampilkan di carousel.
            </DialogDescription>
          </DialogHeader>
          <SlideForm onSubmit={handleCreate} isLoading={creating} />
        </DialogContent>
      </Dialog>

      {/* Edit Dialog */}
      <Dialog
        open={isEditDialogOpen}
        onOpenChange={(open) => !open && dispatch(closeEditDialog())}
      >
        <DialogContent className="max-w-lg max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Edit Slide</DialogTitle>
            <DialogDescription>Ubah detail slide carousel.</DialogDescription>
          </DialogHeader>
          {selectedSlide && (
            <SlideForm
              defaultValues={selectedSlide}
              onSubmit={handleUpdate}
              isLoading={updating}
            />
          )}
        </DialogContent>
      </Dialog>

      {/* Delete Dialog */}
      <Dialog
        open={isDeleteDialogOpen}
        onOpenChange={(open) => !open && dispatch(closeDeleteDialog())}
      >
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Hapus Slide</DialogTitle>
            <DialogDescription>
              Apakah Anda yakin ingin menghapus slide &quot;{selectedSlide?.title}&quot;?
              Tindakan ini tidak dapat dibatalkan.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button variant="outline" onClick={() => dispatch(closeDeleteDialog())}>
              Batal
            </Button>
            <Button variant="destructive" onClick={handleDelete} disabled={deleting}>
              {deleting ? "Menghapus..." : "Hapus"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
