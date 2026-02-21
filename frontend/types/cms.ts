export interface CarouselSlide {
  id: string;
  title: string;
  description: string;
  bg: string;
  fg: string;
  image_url: string | null;
  link_url: string | null;
  link_label: string | null;
  order_index: number;
  is_active: boolean;
}

export interface CreateSlideRequest {
  title: string;
  description: string;
  bg: string;
  fg: string;
  image_url?: string | null;
  link_url?: string | null;
  link_label?: string | null;
  order_index?: number;
}

export type UpdateSlideRequest = Partial<CreateSlideRequest> & {
  is_active?: boolean;
};

export interface UploadImageResponse {
  url: string;
}
