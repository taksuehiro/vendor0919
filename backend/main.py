from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
import models, schemas, auth, database, security, rag_service

# データベーステーブルを作成
try:
    models.Base.metadata.create_all(bind=database.engine)
    print("Database tables created successfully")
except Exception as e:
    print(f"Database error: {e}")

# RAGサービスの初期化
try:
    rag_service_instance = rag_service.RAGService()
    rag_service_instance.initialize()
except Exception as e:
    print(f"RAG service initialization error: {e}")
    rag_service_instance = None

app = FastAPI(title="Vendor Management API", version="1.0.0")

# RAG検索用のスキーマ
class SearchRequest(BaseModel):
    query: str
    k: int = 4
    use_mmr: bool = False

class SearchResponse(BaseModel):
    answer: str
    sources: list

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001"
    ],  # 開発中のフロントエンドの起源を許可
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.options("/{path:path}")
def options_handler(path: str):
    """OPTIONSリクエストを処理"""
    return {"message": "OK"}

@app.get("/")
def root():
    return {"message": "Vendor Management API is running!"}

@app.post("/auth/register", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    # メールアドレスの重複チェック
    db_user = auth.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )
    
    # パスワードをハッシュ化してユーザーを作成
    hashed_password = auth.get_password_hash(user.password)
    db_user = models.User(
        email=user.email,
        password_hash=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.post("/auth/verify", response_model=schemas.UserResponse)
def verify_user(user: schemas.UserLogin, db: Session = Depends(database.get_db)):
    # ユーザー認証
    authenticated_user = auth.authenticate_user(db, user.email, user.password)
    if not authenticated_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    return authenticated_user

# 保護されたエンドポイント
@app.get("/me", response_model=schemas.UserResponse)
def get_current_user_info(current_user: models.User = Depends(security.get_current_user)):
    """現在のユーザー情報を取得"""
    return current_user

@app.get("/protected")
def protected_route(current_user: models.User = Depends(security.get_current_user)):
    """保護されたルートの例"""
    return {
        "message": f"Hello {current_user.email}!",
        "user_id": current_user.id,
        "authenticated": True
    }

# RAG検索エンドポイント
@app.post("/search", response_model=SearchResponse)
def search_documents(
    request: SearchRequest,
    current_user: models.User = Depends(security.get_current_user)
):
    """RAG検索エンドポイント"""
    try:
        # RAG検索を実行
        if rag_service_instance:
            result = rag_service_instance.search(
                query=request.query,
                k=request.k,
                use_mmr=request.use_mmr
            )
        else:
            result = {
                "answer": "RAGサービスが初期化されていません。",
                "sources": []
            }
        
        return SearchResponse(
            answer=result["answer"],
            sources=result["sources"]
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search error: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
