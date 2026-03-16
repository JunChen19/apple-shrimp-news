/**
 * 文章类型定义
 */
export interface Article {
  id: number;
  title: string;
  category: 'llm' | 'industry' | 'politics' | 'finance';
  url: string;
  source: string;
  author?: string | null;
  published_at?: string | null;
  summary?: string | null;
  content?: string | null;
  image_urls?: string[];
  fetched_at?: string | null;
  is_processed?: boolean;
}

export interface CategoryInfo {
  id: string;
  name: string;
  description: string;
  icon: string;
  color: string;
}

export interface ApiResponse<T> {
  data?: T;
  error?: string;
  message?: string;
  status?: string;
}
