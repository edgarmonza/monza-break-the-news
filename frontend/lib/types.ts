/**
 * TypeScript types matching backend API responses
 */

export interface Thread {
  id: string;
  title_id: string; // '@ReformaTributaria'
  display_title: string;
  summary: string;
  trending_score: number;
  article_count: number;
  suggested_questions: string[];
  image_url?: string; // Unsplash background image
  created_at: string;
}

export interface Article {
  id: string;
  title: string;
  url: string;
  source: string;
  author?: string;
  published_at?: string;
  image_url?: string;
}

export interface ThreadDetail extends Thread {
  articles: Article[];
  updated_at: string;
}

export interface FeedResponse {
  threads: Thread[];
  total: number;
  limit: number;
  offset: number;
}

export interface ChatSource {
  title: string;
  source: string;
  url: string;
}

export interface ChatResponse {
  answer: string;
  sources: ChatSource[];
}

export interface ChatRequest {
  question: string;
  thread_id?: string;
}

export interface SearchResult {
  id: string;
  title: string;
  url: string;
  source: string;
  published_at?: string;
}

export interface SearchResponse {
  query: string;
  results: SearchResult[];
  count: number;
}

export interface HealthResponse {
  status: string;
  message: string;
  database?: string;
}

export interface MacroIndicator {
  id: string;
  label: string;
  value: number;
  formatted: string;
  change: number | null;
  change_pct: number | null;
  icon: string;
  category: string;
}

export interface MacroResponse {
  indicators: MacroIndicator[];
  updated_at: string;
}
