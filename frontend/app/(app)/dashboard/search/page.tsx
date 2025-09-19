"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { searchDocuments } from "@/lib/api";

interface SearchResult {
  answer: string;
  sources: Array<{
    title: string;
    content: string;
    score: number;
  }>;
}

export default function SearchPage() {
  const [query, setQuery] = useState("");
  const [k, setK] = useState(4);
  const [useMmr, setUseMmr] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<SearchResult | null>(null);
  const [error, setError] = useState("");

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    setIsLoading(true);
    setError("");
    setResult(null);

    try {
      const response = await searchDocuments(query, k, useMmr);
      setResult(response);
    } catch (error: unknown) {
      if (error instanceof Error) {
        setError(error.message || "検索中にエラーが発生しました。");
      } else {
        setError("検索中にエラーが発生しました。");
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-gray-900">AI検索</h1>
            <p className="mt-2 text-gray-600">
              LangChainとOpenAIを活用した高度な文書検索機能
            </p>
          </div>

          {/* 検索フォーム */}
          <Card className="mb-8">
            <CardHeader>
              <CardTitle>検索クエリ</CardTitle>
              <CardDescription>
                ベンダー管理、調達プロセス、サプライヤー関係管理に関する質問を入力してください
              </CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleSearch} className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="query">検索クエリ</Label>
                  <Input
                    id="query"
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    placeholder="例: ベンダー選定のベストプラクティスは？"
                    required
                  />
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="k">取得する文書数 (k)</Label>
                    <Input
                      id="k"
                      type="number"
                      min="1"
                      max="10"
                      value={k}
                      onChange={(e) => setK(parseInt(e.target.value) || 4)}
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="mmr">MMR (Maximal Marginal Relevance)</Label>
                    <div className="flex items-center space-x-2">
                      <input
                        id="mmr"
                        type="checkbox"
                        checked={useMmr}
                        onChange={(e) => setUseMmr(e.target.checked)}
                        className="h-4 w-4 text-primary focus:ring-primary border-input rounded"
                      />
                      <Label htmlFor="mmr" className="text-sm">
                        多様性を重視した検索
                      </Label>
                    </div>
                  </div>
                </div>

                <Button
                  type="submit"
                  disabled={isLoading || !query.trim()}
                  className="w-full"
                >
                  {isLoading ? "検索中..." : "検索実行"}
                </Button>
              </form>
            </CardContent>
          </Card>

          {/* エラー表示 */}
          {error && (
            <Card className="mb-8 border-red-200 bg-red-50">
              <CardContent className="pt-6">
                <p className="text-red-600">{error}</p>
              </CardContent>
            </Card>
          )}

          {/* 検索結果 */}
          {result && (
            <div className="space-y-6">
              {/* 回答 */}
              <Card>
                <CardHeader>
                  <CardTitle>AI回答</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="prose max-w-none">
                    <p className="whitespace-pre-wrap">{result.answer}</p>
                  </div>
                </CardContent>
              </Card>

              {/* 参照文書 */}
              {result.sources && result.sources.length > 0 && (
                <Card>
                  <CardHeader>
                    <CardTitle>参照文書</CardTitle>
                    <CardDescription>
                      回答の根拠となった文書の一覧
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      {result.sources.map((source, index) => (
                        <div
                          key={index}
                          className="border rounded-lg p-4 bg-gray-50"
                        >
                          <div className="flex justify-between items-start mb-2">
                            <h4 className="font-medium text-gray-900">
                              {source.title}
                            </h4>
                            <span className="text-sm text-gray-500">
                              スコア: {source.score.toFixed(2)}
                            </span>
                          </div>
                          <p className="text-sm text-gray-700">
                            {source.content}
                          </p>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              )}
            </div>
          )}

          {/* サンプルクエリ */}
          <Card className="mt-8">
            <CardHeader>
              <CardTitle>サンプルクエリ</CardTitle>
              <CardDescription>
                以下のような質問を試してみてください
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <h4 className="font-medium">ベンダー管理</h4>
                  <ul className="text-sm text-gray-600 space-y-1">
                    <li>• ベンダー選定のベストプラクティスは？</li>
                    <li>• パフォーマンス評価の指標は？</li>
                    <li>• リスク管理の方法は？</li>
                  </ul>
                </div>
                <div className="space-y-2">
                  <h4 className="font-medium">調達プロセス</h4>
                  <ul className="text-sm text-gray-600 space-y-1">
                    <li>• 調達の基本フローは？</li>
                    <li>• RFP作成のポイントは？</li>
                    <li>• 評価基準の設定方法は？</li>
                  </ul>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
