from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlmodel import Session, create_engine, select
from app.models.models import Match, Group, Prediction, User, SQLModel
from app.services.scoring import calculate_points
from app.core.security import get_password_hash, verify_password, create_access_token
from typing import List
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")
engine = create_engine(DATABASE_URL)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_session():
    with Session(engine) as session:
        yield session

app = FastAPI(title="Polla WC26 API")

@app.post("/register")
def register(user_data: User, session: Session = Depends(get_session)):
    # Verificar si el usuario ya existe
    existing_user = session.exec(select(User).where(User.username == user_data.username)).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")

    # Hashear contraseña y guardar
    user_data.hashed_password = get_password_hash(user_data.hashed_password)
    session.add(user_data)
    session.commit()
    session.refresh(user_data)
    return {"status": "success", "user_id": user_data.id}

@app.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_session)):
    user = session.exec(select(User).where(User.username == form_data.username)).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/matches", response_model=List[Match])
def get_matches(session: Session = Depends(get_session)):
    return session.exec(select(Match)).all()

@app.post("/predictions/bulk")
def create_bulk_predictions(predictions: List[Prediction], session: Session = Depends(get_session)):
    # Nota: Aquí se debería añadir lógica de validación de tiempo (bloqueo 5 min)
    # y verificación de usuario/grupo.
    for pred in predictions:
        session.add(pred)
    session.commit()
    return {"status": "success", "count": len(predictions)}

@app.get("/test-scoring")
def test_scoring(p1: int, p2: int, a1: int, a2: int, knockout: bool = False):
    pts = calculate_points(p1, p2, a1, a2, knockout)
    return {"points": pts}
