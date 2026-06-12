from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, create_engine, select
from app.models.models import Match, Group, Prediction, User, SQLModel
from app.services.scoring import calculate_points
from app.core.security import get_password_hash, verify_password, create_access_token
from typing import List
import os
from datetime import datetime, timedelta
from uuid import UUID
import uuid

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

from jose import jwt, JWTError
from app.core.security import SECRET_KEY, ALGORITHM

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

from app.schemas.user import UserProfileUpdate, UserRead, ForgotPasswordRequest, ResetPasswordRequest
from app.schemas.group import GroupCreate, GroupRead, GroupJoin, GroupConfigurationRead, GroupConfigurationUpdate
from app.models.models import UserGroupLink, GroupConfiguration
import secrets
import string

@app.get("/users/me", response_model=UserRead)
def get_user_me(current_user: User = Depends(get_current_user)):
    return current_user

@app.put("/users/me", response_model=UserRead)
def update_user_me(
    user_update: UserProfileUpdate, 
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    if user_update.full_name is not None:
        current_user.full_name = user_update.full_name
    if user_update.email is not None:
        # Verificar si el email ya existe en otro usuario
        existing = session.exec(select(User).where(User.email == user_update.email, User.id != current_user.id)).first()
        if existing:
            raise HTTPException(status_code=400, detail="Email already in use")
        current_user.email = user_update.email
    if user_update.avatar_url is not None:
        current_user.avatar_url = user_update.avatar_url
    
    session.add(current_user)
    session.commit()
    session.refresh(current_user)
    return current_user

@app.post("/forgot-password")
def forgot_password(request: ForgotPasswordRequest, session: Session = Depends(get_session)):
    user = session.exec(select(User).where(User.email == request.email)).first()
    if not user:
        # Por seguridad, no revelamos si el email existe
        return {"message": "Si el correo está registrado, recibirás un código de recuperación."}
    
    token = secrets.token_urlsafe(32)
    user.reset_token = token
    user.reset_token_expires = datetime.utcnow() + timedelta(hours=1)
    
    session.add(user)
    session.commit()
    
    # SIMULACIÓN DE ENVÍO DE CORREO
    print(f"\n[EMAIL SIMULATION] Para: {user.email}")
    print(f"[EMAIL SIMULATION] Tu token de recuperación es: {token}\n")
    
    return {"message": "Si el correo está registrado, recibirás un código de recuperación."}

@app.post("/reset-password")
def reset_password(request: ResetPasswordRequest, session: Session = Depends(get_session)):
    user = session.exec(
        select(User).where(
            User.reset_token == request.token, 
            User.reset_token_expires > datetime.utcnow()
        )
    ).first()
    
    if not user:
        raise HTTPException(status_code=400, detail="Token inválido o expirado")
    
    user.hashed_password = get_password_hash(request.new_password)
    user.reset_token = None
    user.reset_token_expires = None
    
    session.add(user)
    session.commit()
    return {"message": "Contraseña actualizada exitosamente"}

@app.post("/groups", response_model=GroupRead)
def create_group(
    group_data: GroupCreate, 
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    # Generar código de invitación único de 6 caracteres
    alphabet = string.ascii_uppercase + string.digits
    while True:
        code = ''.join(secrets.choice(alphabet) for _ in range(6))
        existing = session.exec(select(Group).where(Group.invite_code == code)).first()
        if not existing:
            break
    
    # Crear grupo
    new_group = Group(
        name=group_data.name,
        invite_code=code,
        creator_id=current_user.id
    )
    session.add(new_group)
    session.commit()
    session.refresh(new_group)
    
    # Inicializar configuración por defecto
    config = GroupConfiguration(group_id=new_group.id)
    session.add(config)
    
    # Agregar al creador como miembro admin
    member = UserGroupLink(user_id=current_user.id, group_id=new_group.id, role="admin")
    session.add(member)
    
    session.commit()
    return new_group

@app.post("/groups/join")
def join_group(
    join_data: GroupJoin, 
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    group = session.exec(select(Group).where(Group.invite_code == join_data.invite_code)).first()
    if not group:
        raise HTTPException(status_code=404, detail="Código de invitación inválido")
    
    # Verificar si ya es miembro
    existing = session.exec(
        select(UserGroupLink).where(
            UserGroupLink.user_id == current_user.id, 
            UserGroupLink.group_id == group.id
        )
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Ya eres miembro de este grupo")
    
    member = UserGroupLink(user_id=current_user.id, group_id=group.id)
    session.add(member)
    session.commit()
    return {"status": "success", "group_name": group.name}

@app.get("/groups", response_model=List[GroupRead])
def get_my_groups(current_user: User = Depends(get_current_user)):
    return current_user.groups

@app.get("/groups/{group_id}/config", response_model=GroupConfigurationRead)
def get_group_config(
    group_id: UUID, 
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    # Verificar que el usuario pertenece al grupo
    member = session.exec(
        select(UserGroupLink).where(
            UserGroupLink.user_id == current_user.id, 
            UserGroupLink.group_id == group_id
        )
    ).first()
    if not member:
        raise HTTPException(status_code=403, detail="No tienes acceso a este grupo")
    
    config = session.exec(select(GroupConfiguration).where(GroupConfiguration.group_id == group_id)).first()
    if not config:
        raise HTTPException(status_code=404, detail="Configuración no encontrada")
    return config

@app.put("/groups/{group_id}/config", response_model=GroupConfigurationRead)
def update_group_config(
    group_id: UUID,
    config_update: GroupConfigurationUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    group = session.get(Group, group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Grupo no encontrado")
    
    # Solo el creador puede editar la configuración
    if group.creator_id != current_user.id:
        raise HTTPException(status_code=403, detail="Solo el creador puede modificar las reglas")
    
    config = session.exec(select(GroupConfiguration).where(GroupConfiguration.group_id == group_id)).first()
    
    for key, value in config_update.model_dump(exclude_unset=True).items():
        setattr(config, key, value)
    
    session.add(config)
    session.commit()
    session.refresh(config)
    return config

@app.get("/matches", response_model=List[Match])
def get_matches(session: Session = Depends(get_session)):
    return session.exec(select(Match)).all()

@app.get("/predictions/my")
def get_my_predictions(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    preds = session.exec(select(Prediction).where(Prediction.user_id == current_user.id)).all()
    return preds

@app.post("/predictions/bulk")
def create_bulk_predictions(
    predictions_data: List[dict], 
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    # Por ahora, si no hay grupos creados, usaremos un ID nulo o uno por defecto
    # En una versión final, el frontend enviaría el group_id real.
    
    for item in predictions_data:
        match_id = uuid.UUID(item["match_id"])
        group_id = uuid.UUID(item.get("group_id", "00000000-0000-0000-0000-000000000000"))
        
        # Buscar si ya existe una predicción para este usuario y partido
        existing_prediction = session.exec(
            select(Prediction).where(
                Prediction.user_id == current_user.id,
                Prediction.match_id == match_id,
                Prediction.group_id == group_id
            )
        ).first()

        if existing_prediction:
            # Actualizar la existente
            existing_prediction.predicted_goals1 = item["predicted_goals1"]
            existing_prediction.predicted_goals2 = item["predicted_goals2"]
            existing_prediction.updated_at = datetime.utcnow()
            session.add(existing_prediction)
        else:
            # Crear una nueva
            prediction = Prediction(
                user_id=current_user.id,
                match_id=match_id,
                group_id=group_id,
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
