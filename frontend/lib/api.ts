/**
 * API client for Colombia News backend
 */
import {
  Thread,
  ThreadDetail,
  FeedResponse,
  ChatRequest,
  ChatResponse,
  SearchResponse,
  HealthResponse,
  MacroResponse,
} from './types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
    this.name = 'ApiError';
  }
}

async function fetchApi<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;

  try {
    const response = await fetch(url, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options?.headers,
      },
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
      throw new ApiError(response.status, error.detail || 'Request failed');
    }

    return response.json();
  } catch (error) {
    if (error instanceof ApiError) {
      throw error;
    }
    throw new Error('Network error: Unable to connect to API');
  }
}

export const api = {
  /**
   * Health check
   */
  health: async (): Promise<HealthResponse> => {
    return fetchApi<HealthResponse>('/health');
  },

  /**
   * Get news feed
   */
  getFeed: async (params?: {
    limit?: number;
    offset?: number;
    min_score?: number;
  }): Promise<FeedResponse> => {
    const searchParams = new URLSearchParams();
    if (params?.limit) searchParams.set('limit', params.limit.toString());
    if (params?.offset) searchParams.set('offset', params.offset.toString());
    if (params?.min_score) searchParams.set('min_score', params.min_score.toString());

    const query = searchParams.toString();
    return fetchApi<FeedResponse>(`/api/feed${query ? `?${query}` : ''}`);
  },

  /**
   * Get thread detail
   */
  getThread: async (threadId: string): Promise<ThreadDetail> => {
    return fetchApi<ThreadDetail>(`/api/thread/${threadId}`);
  },

  /**
   * Chat with AI
   */
  chat: async (request: ChatRequest): Promise<ChatResponse> => {
    return fetchApi<ChatResponse>('/api/chat', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  },

  /**
   * Search articles
   */
  getMacro: async (): Promise<MacroResponse> => {
    return fetchApi<MacroResponse>('/api/macro');
  },

  search: async (query: string, limit: number = 10): Promise<SearchResponse> => {
    const searchParams = new URLSearchParams({
      query,
      limit: limit.toString(),
    });
    return fetchApi<SearchResponse>(`/api/search?${searchParams}`);
  },
};

export { ApiError };
