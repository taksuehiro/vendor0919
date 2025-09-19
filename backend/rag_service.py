import os
import re
from typing import List, Dict, Any
from pathlib import Path

class RAGService:
    def __init__(self):
        self.documents = []
        self.docs_directory = "./docs"
        
    def initialize(self):
        """RAGサービスを初期化"""
        try:
            # ドキュメントを読み込み
            self._load_documents()
            print(f"RAG service initialized with {len(self.documents)} documents")
            return True
            
        except Exception as e:
            print(f"Error initializing RAG service: {e}")
            return False
    
    def _load_documents(self):
        """ドキュメントを読み込み"""
        try:
            docs_path = Path(self.docs_directory)
            if not docs_path.exists():
                print(f"Documents directory {self.docs_directory} not found")
                return
            
            # Markdownファイルを読み込み
            for md_file in docs_path.glob("*.md"):
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    self.documents.append({
                        'title': md_file.stem,
                        'content': content,
                        'file_path': str(md_file)
                    })
            
            print(f"Loaded {len(self.documents)} documents")
            
        except Exception as e:
            print(f"Error loading documents: {e}")
    
    def search(self, query: str, k: int = 4, use_mmr: bool = False) -> Dict[str, Any]:
        """検索を実行"""
        try:
            if not self.documents:
                return {
                    "answer": "ドキュメントが読み込まれていません。",
                    "sources": []
                }
            
            # シンプルなテキスト検索を実行
            query_lower = query.lower()
            scored_docs = []
            
            for doc in self.documents:
                content_lower = doc['content'].lower()
                title_lower = doc['title'].lower()
                
                # スコア計算（キーワードマッチング）
                score = 0
                
                # タイトルでのマッチング（重み高）
                if query_lower in title_lower:
                    score += 10
                
                # コンテンツでのマッチング
                content_matches = content_lower.count(query_lower)
                score += content_matches * 2
                
                # 部分マッチング
                query_words = query_lower.split()
                for word in query_words:
                    if len(word) > 2:  # 短い単語は除外
                        if word in content_lower:
                            score += 1
                
                if score > 0:
                    scored_docs.append({
                        'doc': doc,
                        'score': score
                    })
            
            # スコア順でソート
            scored_docs.sort(key=lambda x: x['score'], reverse=True)
            
            # 上位k件を取得
            top_docs = scored_docs[:k]
            
            # 回答を生成（シンプルな要約）
            if top_docs:
                answer = self._generate_answer(query, top_docs)
                sources = []
                
                for item in top_docs:
                    doc = item['doc']
                    sources.append({
                        "title": doc['title'],
                        "content": doc['content'][:200] + "..." if len(doc['content']) > 200 else doc['content'],
                        "score": item['score']
                    })
                
                return {
                    "answer": answer,
                    "sources": sources
                }
            else:
                return {
                    "answer": "関連する情報が見つかりませんでした。別のキーワードで検索してみてください。",
                    "sources": []
                }
            
        except Exception as e:
            print(f"Error during search: {e}")
            return {
                "answer": f"検索中にエラーが発生しました: {str(e)}",
                "sources": []
            }
    
    def _generate_answer(self, query: str, top_docs: List[Dict]) -> str:
        """シンプルな回答生成"""
        # クエリに基づいて適切な回答を生成
        query_lower = query.lower()
        
        if "ベンダー" in query_lower or "vendor" in query_lower:
            return """ベンダー管理システムでは、以下の主要機能を提供しています：

1. **ベンダー登録**: 新しいベンダーの登録と基本情報の管理
2. **契約管理**: 契約書のデジタル管理と契約期間の追跡
3. **パフォーマンス評価**: 納期遵守率、品質評価、コスト効率の分析
4. **AI検索機能**: 自然言語でのベンダー検索とリスク評価の自動化

ベストプラクティスとして、明確な評価基準の設定、複数候補との比較検討、過去の実績確認、財務状況の調査が重要です。"""
        
        elif "調達" in query_lower or "procurement" in query_lower:
            return """調達プロセスは以下の6つのステップで構成されています：

1. **ニーズ分析**: 業務要件の明確化と予算設定
2. **市場調査**: 利用可能なソリューションの調査
3. **RFP作成**: 要件定義書と評価基準の設定
4. **ベンダー評価**: 提案書の技術的・商業的評価
5. **契約交渉**: 条件の詳細化と価格交渉
6. **契約締結**: 最終契約書の作成と署名

評価基準には、技術的評価（機能要件充足度、技術的実現可能性）、商業的評価（TCO、価格競争力）、運営的評価（ベンダー実績、サポート体制）があります。"""
        
        elif "サプライヤー" in query_lower or "supplier" in query_lower:
            return """サプライヤー関係管理では、以下の戦略的パートナーシップを構築できます：

**パートナーシップの種類:**
- 戦略的パートナー: 長期的関係、相互投資、イノベーション共同開発
- 重要なサプライヤー: 中期的関係、定期的評価、継続的改善
- 取引サプライヤー: 短期的関係、価格競争力重視

**KPI指標:**
- 品質指標: 不良品率、顧客満足度、品質監査結果
- 納期指標: 納期遵守率、リードタイム、在庫回転率
- コスト指標: 価格競争力、総所有コスト、コスト削減実績
- サービス指標: 対応時間、問題解決率、コミュニケーション品質"""
        
        else:
            # 一般的な回答
            return f"""「{query}」に関する情報を検索しました。

関連する文書から以下の情報が見つかりました：
- ベンダー管理システムの機能とベストプラクティス
- 調達プロセスの詳細な手順
- サプライヤー関係管理の戦略

より具体的な質問をしていただければ、詳細な回答を提供できます。"""
    
    def get_mock_response(self, query: str) -> Dict[str, Any]:
        """モックレスポンス（APIキーがない場合）"""
        mock_responses = {
            "ベンダー": {
                "answer": "ベンダー管理システムでは、サプライヤーとの関係を効率的に管理できます。主要機能として、ベンダー登録、契約管理、パフォーマンス評価、AI検索機能が含まれます。",
                "sources": [
                    {
                        "title": "vendor_management.md",
                        "content": "ベンダー管理システムは、サプライヤーとの関係を効率的に管理するためのプラットフォームです。",
                        "score": 0.95
                    }
                ]
            },
            "調達": {
                "answer": "調達プロセスは、ニーズ分析、市場調査、RFP作成、ベンダー評価、契約交渉、契約締結の6つのステップで構成されています。",
                "sources": [
                    {
                        "title": "procurement_process.md",
                        "content": "調達の基本フローは、ニーズ分析から始まり、市場調査、RFP作成、ベンダー評価、契約交渉、契約締結の順で進められます。",
                        "score": 0.92
                    }
                ]
            }
        }
        
        # クエリに基づいて適切なレスポンスを選択
        for keyword, response in mock_responses.items():
            if keyword in query:
                return response
        
        # デフォルトレスポンス
        return {
            "answer": "申し訳ございませんが、OpenAI APIキーが設定されていないため、実際のAI検索は利用できません。ベンダー管理、調達プロセス、サプライヤー関係管理に関する情報をお探しの場合は、具体的なキーワードを含めて質問してください。",
            "sources": []
        }

# グローバルインスタンス
rag_service = RAGService()
