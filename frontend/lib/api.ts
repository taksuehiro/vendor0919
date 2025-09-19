import { getSession } from "next-auth/react";

export const API_BASE = process.env.NEXT_PUBLIC_API_BASE!;

// 認証付きAPI呼び出し用のヘルパー関数
export async function authenticatedFetch(url: string, options: RequestInit = {}) {
  const session = await getSession();
  
  if (!session?.accessToken) {
    throw new Error("No access token available");
  }

  const headers = {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${session.accessToken}`,
    ...options.headers,
  };

  const response = await fetch(`${API_BASE}${url}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    if (response.status === 401) {
      // 認証エラーの場合はログインページにリダイレクト
      window.location.href = '/login';
      return;
    }
    throw new Error(`API error: ${response.status}`);
  }

  return response.json();
}

// 保護されたAPIエンドポイントの呼び出し例
export async function getCurrentUser() {
  return authenticatedFetch('/me');
}

export async function getProtectedData() {
  return authenticatedFetch('/protected');
}

// RAG検索機能
export async function searchDocuments(query: string, k: number = 4, useMmr: boolean = false) {
  return authenticatedFetch('/search', {
    method: 'POST',
    body: JSON.stringify({
      query,
      k,
      use_mmr: useMmr
    })
  });
}
