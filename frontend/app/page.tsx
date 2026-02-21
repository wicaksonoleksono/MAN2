"use client";

import { useEffect, useState } from "react";
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
import { Button } from "@/components/ui/button";
import { BookOpen, Users, Briefcase } from "lucide-react";
import Link from "next/link";
import type { CarouselSlide } from "@/types/cms";



const layananCards = [
  {
    title: "Layanan Akademik",
    description:
      "Informasi kurikulum, jadwal pelajaran, nilai, dan rapor siswa MAN 2 Yogyakarta.",
    icon: BookOpen,
    href: undefined as string | undefined,
  },
  {
    title: "Layanan Publik",
    description:
      "Informasi umum, pengumuman, dan layanan publik bagi masyarakat dan orang tua.",
    icon: Users,
    href: "https://man2yogyakarta.sch.id/",
  },
  {
    title: "Layanan PTK",
    description:
      "Layanan bagi Pendidik dan Tenaga Kependidikan: absensi, tugas, dan administrasi.",
    icon: Briefcase,
    href: undefined as string | undefined,
  },
];

export default function IndexPage() {
  const [slides, setSlides] = useState<CarouselSlide[]>([]);

  useEffect(() => {
    fetch("/data.json")
      .then((res) => (res.ok ? res.json() : []))
      .then((data: CarouselSlide[]) => {
        setSlides(data.filter((s) => s.is_active));
      })
      .catch(() => {});
  }, []);

  const carouselSlides = slides;

  return (
    <main className="flex flex-col gap-8 px-4 py-8 md:px-8 lg:px-16">
      {/* Hero Carousel */}
      <Carousel opts={{ loop: true }} className="w-full">
        <CarouselContent>
          {carouselSlides.map((slide) => (
            <CarouselItem key={slide.id}>
              <Card className={`${slide.bg} ${slide.fg} border-none`}>
                <CardContent className="flex min-h-[360px] flex-col items-center justify-center p-6 text-center md:min-h-[480px]">
                  {slide.image_url && (
                    <img
                      src={slide.image_url}
                      alt={slide.title}
                      className="mb-6 max-h-32 object-contain"
                    />
                  )}
                  <h2 className="text-2xl font-bold md:text-4xl">
                    {slide.title}
                  </h2>
                  <p className="mt-3 max-w-2xl text-base md:text-lg opacity-90">
                    {slide.description}
                  </p>
                  {slide.link_url && slide.link_label && (
                    <Button asChild variant="secondary" className="mt-6">
                      <Link href={slide.link_url}>{slide.link_label}</Link>
                    </Button>
                  )}
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
          const card = (
            <Card
              key={item.title}
              className={`transition-shadow hover:shadow-lg${item.href ? " cursor-pointer" : ""}`}
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
          return item.href ? (
            <a key={item.title} href={item.href} target="_blank" rel="noopener noreferrer">
              {card}
            </a>
          ) : (
            card
          );
        })}
      </div>
    </main>
  );
}
