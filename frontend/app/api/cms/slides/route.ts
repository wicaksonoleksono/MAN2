import { NextResponse } from "next/server";
import { readSlides, writeSlides } from "@/lib/cms-store";
import type { CreateSlideRequest } from "@/types/cms";
import { randomUUID } from "crypto";

export async function GET() {
  const slides = readSlides();
  return NextResponse.json(slides);
}

export async function POST(request: Request) {
  const body = (await request.json()) as CreateSlideRequest;
  const slides = readSlides();

  const newSlide = {
    id: randomUUID(),
    title: body.title,
    description: body.description,
    bg: body.bg,
    fg: body.fg,
    image_url: body.image_url ?? null,
    link_url: body.link_url ?? null,
    link_label: body.link_label ?? null,
    order_index: body.order_index ?? slides.length,
    is_active: true,
  };

  slides.push(newSlide);
  writeSlides(slides);

  return NextResponse.json(newSlide, { status: 201 });
}
