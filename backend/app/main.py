from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
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

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # En producción se debe restringir a los dominios del frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

from jose import jwt
from app.core.security import SECRET_KEY, ALGORITHM
import uuid

# ... (código anterior)

async def get_current_user(token: str = Depends(oauth2_scheme), session: Session = Depends(get_session)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = session.exec(select(User).where(User.username == username)).first()
    if user is None:
        raise credentials_exception
    return user

@app.get("/matches", response_model=List[Match])
def get_matches(session: Session = Depends(get_session)):
    return session.exec(select(Match)).all()

@app.post("/predictions/bulk")
def create_bulk_predictions(
    predictions_data: List[dict], 
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    # Por ahora, si no hay grupos creados, usaremos un ID nulo o uno por defecto
    # En una versión final, el frontend enviaría el group_id real.
    
    for item in predictions_data:
        # Convertir strings a UUIDs y asignar el usuario actual
        match_id = uuid.UUID(item["match_id"])
        
        # Buscar si ya existe una predicción para este usuario/partido/grupo
        # (Para simplificar el prototipo, permitiremos múltiples por ahora o actualizaremos)
        
        prediction = Prediction(
            user_id=current_user.id,
            match_id=match_id,
            group_id=uuid.UUID(item.get("group_id", "00000000-0000-0000-0000-000000000000")),
            predicted_goals1=item["predicted_goals1"],
            predicted_goals2=item["predicted_goals2"]
        )
        session.add(prediction)
    
    session.commit()
    return {"status": "success", "count": len(predictions_data)}

@app.get("/test-scoring")
def test_scoring(p1: int, p2: int, a1: int, a2: int, knockout: bool = False):
    pts = calculate_points(p1, p2, a1, a2, knockout)
    return {"points": pts}
