import os
import secrets
import argparse
from datetime import datetime, timedelta, timezone
from sqlmodel import Session, create_engine, select
from app.models.models import User

def generate_token(username: str):
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("Error: DATABASE_URL environment variable is not set.")
        return

    # In Railway, DATABASE_URL usually starts with postgres://
    # SQLModel/SQLAlchemy might need postgresql://
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)

    engine = create_engine(db_url)
    
    with Session(engine) as session:
        statement = select(User).where(User.username == username)
        user = session.exec(statement).first()
        
        if not user:
            print(f"Error: User '{username}' not found.")
            return

        token = secrets.token_urlsafe(32)
        user.reset_token = token
        # Using utcnow() to match app convention
        user.reset_token_expires = datetime.utcnow() + timedelta(hours=1)
        
        session.add(user)
        session.commit()
        
        frontend_url = os.getenv("FRONTEND_URL", "https://tu-app-frontend.railway.app")
        reset_link = f"{frontend_url}/reset-password?token={token}"
        
        print("\n" + "="*50)
        print(f"RECUPERACIÓN DE CONTRASEÑA")
        print("="*50)
        print(f"Usuario:    {username}")
        print(f"Email:      {user.email}")
        print(f"Token:      {token}")
        print("-" * 50)
        print(f"Link de recuperación:")
        print(f"{reset_link}")
        print("="*50)
        print("El token expirará en 1 hora.\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Genera un token de recuperación para un usuario.")
    parser.add_argument("username", help="Nombre de usuario (username)")
    args = parser.parse_args()
    
    generate_token(args.username)
