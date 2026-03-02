export interface MessageResponse {
  message: string;
}

export interface PaginationParams {
  skip: number;
  limit: number;
  search?: string;
}
