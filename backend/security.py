from jose import JWTError, jwt
from fastapi import Header, HTTPException, Depends
from sqlalchemy.orm import Session
import os
import database
import models

# 環境変数からシークレットを取得
SECRET = os.getenv("NEXTAUTH_SECRET", "your-secret-key-here-change-in-production")
ALGORITHM = "HS256"

def get_current_user(authorization: str = Header(...), db: Session = Depends(database.get_db)):
    """AuthorizationヘッダのBearer JWTからユーザー情報を取得"""
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid auth header")
    
    token = authorization[len("Bearer "):]
    
    try:
        payload = jwt.decode(token, SECRET, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")  # NextAuthのJWTでは"sub"にユーザーIDが入る
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token payload")
        
        # データベースからユーザー情報を取得
        user = db.query(models.User).filter(models.User.id == int(user_id)).first()
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")
        
        return user
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
