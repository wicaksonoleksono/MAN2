"use client";

import {
  Carousel,
  CarouselContent,
  CarouselItem,
  CarouselPrevious,
  CarouselNext,
} from "@/components/ui/carousel";
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
} from "@/components/ui/card";
import { BookOpen, Users, Briefcase } from "lucide-react";

const carouselSlides = [
  {
    title: "Selamat Datang di SIMANDAYA",
    description:
      "Sistem Informasi Manajemen Data Madrasah Aliyah - MAN 2 Yogyakarta",
    bg: "bg-primary",
    fg: "text-primary-foreground",
  },
  {
    title: "Layanan Digital Terpadu",
    description:
      "Akses informasi akademik, absensi, dan layanan sekolah dalam satu platform",
    bg: "bg-secondary",
    fg: "text-secondary-foreground",
  },
  {
    title: "Transparan dan Akuntabel",
    description:
      "Mendukung pengelolaan madrasah yang modern, transparan, dan akuntabel",
    bg: "bg-accent",
    fg: "text-accent-foreground",
  },
];

const layananCards = [
  {
    title: "Layanan Akademik",
    description:
      "Informasi kurikulum, jadwal pelajaran, nilai, dan rapor siswa MAN 2 Yogyakarta.",
    icon: BookOpen,
  },
  {
    title: "Layanan Publik",
    description:
      "Informasi umum, pengumuman, dan layanan publik bagi masyarakat dan orang tua.",
    icon: Users,
  },
  {
    title: "Layanan PTK",
    description:
      "Layanan bagi Pendidik dan Tenaga Kependidikan: absensi, tugas, dan administrasi.",
    icon: Briefcase,
  },
];

export default function IndexPage() {
  return (
    <main className="flex flex-col gap-8 px-4 py-8 md:px-8 lg:px-16">
      {/* Hero Carousel */}
      <Carousel opts={{ loop: true }} className="w-full">
        <CarouselContent>
          {carouselSlides.map((slide) => (
            <CarouselItem key={slide.title}>
              <Card className={`${slide.bg} ${slide.fg} border-none`}>
                <CardContent className="flex min-h-[360px] flex-col items-center justify-center p-6 text-center md:min-h-[480px]">
                  <h2 className="text-2xl font-bold md:text-4xl">
                    {slide.title}
                  </h2>
                  <p className="mt-3 max-w-2xl text-base md:text-lg opacity-90">
                    {slide.description}
                  </p>
                </CardContent>
              </Card>
            </CarouselItem>
          ))}
        </CarouselContent>
        <CarouselPrevious className="left-4 md:left-6" />
        <CarouselNext className="right-4 md:right-6" />
      </Carousel>

      {/* Layanan Cards */}
      <div className="grid gap-6 md:grid-cols-3">
        {layananCards.map((item) => {
          const Icon = item.icon;
          return (
            <Card
              key={item.title}
              className="transition-shadow hover:shadow-lg"
            >
              <CardHeader className="items-center text-center">
                <div className="mb-2 flex h-12 w-12 items-center justify-center rounded-full bg-primary/10 text-primary">
                  <Icon className="h-6 w-6" />
                </div>
                <CardTitle className="text-lg">{item.title}</CardTitle>
              </CardHeader>
              <CardContent>
                <CardDescription className="text-center">
                  {item.description}
                </CardDescription>
              </CardContent>
            </Card>
          );
        })}
      </div>
    </main>
  );
}
