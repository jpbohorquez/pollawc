from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, create_engine, select, delete
from app.models.models import Match, Group, Prediction, User, SQLModel
from app.schemas.match import MatchRead

# ... (rest of imports)
from app.services.scoring import calculate_points
from app.core.security import get_password_hash, verify_password, create_access_token
from typing import List
import os
from dotenv import load_dotenv

# Cargar variables de entorno desde backend/.env.local (si existe) para desarrollo local
load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env.local"))

from datetime import datetime, timedelta, timezone

# ... (rest of imports)
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

from app.core.emails import send_reset_password_email
from fastapi import BackgroundTasks

# ... (código existente)

@app.post("/forgot-password")
async def forgot_password(request: ForgotPasswordRequest, background_tasks: BackgroundTasks, session: Session = Depends(get_session)):
    user = session.exec(select(User).where(User.email == request.email)).first()
    if not user:
        # Por seguridad, no revelamos si el email existe
        return {"message": "Si el correo está registrado, recibirás un código de recuperación."}
    
    token = secrets.token_urlsafe(32)
    user.reset_token = token
    user.reset_token_expires = datetime.utcnow() + timedelta(hours=1)
    
    session.add(user)
    session.commit()
    
    # Enviar correo en segundo plano
    background_tasks.add_task(send_reset_password_email, user.email, token)
    
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
        if not existing.is_active:
            existing.is_active = True
            session.add(existing)
            session.commit()
            return {"status": "success", "group_name": group.name}
        raise HTTPException(status_code=400, detail="Ya eres miembro de este grupo")
    
    member = UserGroupLink(user_id=current_user.id, group_id=group.id)
    session.add(member)
    session.commit()
    return {"status": "success", "group_name": group.name}

@app.get("/groups", response_model=List[GroupRead])
def get_my_groups(session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    statement = select(Group).join(UserGroupLink).where(
        UserGroupLink.user_id == current_user.id,
        UserGroupLink.is_active == True
    )
    return session.exec(statement).all()

@app.post("/groups/{group_id}/leave")
def leave_group(
    group_id: UUID,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    link = session.exec(
        select(UserGroupLink).where(
            UserGroupLink.user_id == current_user.id, 
            UserGroupLink.group_id == group_id
        )
    ).first()
    
    if not link:
        raise HTTPException(status_code=404, detail="No eres miembro de este grupo")
        
    link.is_active = False
    session.add(link)
    session.commit()
    return {"status": "success"}

@app.delete("/groups/{group_id}")
def delete_group(
    group_id: UUID,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    group = session.get(Group, group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Grupo no encontrado")
        
    if group.creator_id != current_user.id:
        raise HTTPException(status_code=403, detail="Solo el creador puede eliminar el grupo")
    
    # Eliminar en cascada
    session.exec(delete(Prediction).where(Prediction.group_id == group_id))
    session.exec(delete(UserGroupLink).where(UserGroupLink.group_id == group_id))
    session.exec(delete(GroupConfiguration).where(GroupConfiguration.group_id == group_id))
    session.delete(group)
    session.commit()
    
    return {"status": "success"}

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

def map_match_to_read(match: Match) -> MatchRead:
    tz_gmt5 = timezone(timedelta(hours=-5))
    start_at_utc = match.start_at.replace(tzinfo=tz_gmt5).astimezone(timezone.utc)
    now_utc = datetime.now(timezone.utc)
    is_locked = (start_at_utc - now_utc).total_seconds() / 60 < 5
    return MatchRead(
        id=match.id,
        team1=match.team1,
        team2=match.team2,
        group_name=match.group_name,
        stadium=match.stadium,
        start_at=start_at_utc,
        phase=match.phase,
        actual_goals1=match.actual_goals1,
        actual_goals2=match.actual_goals2,
        is_finished=match.is_finished,
        is_locked=is_locked
    )

@app.get("/matches", response_model=List[MatchRead])
def get_matches(session: Session = Depends(get_session)):
    matches = session.exec(select(Match)).all()
    return [map_match_to_read(m) for m in matches]

from app.schemas.leaderboard import LeaderboardRead, LeaderboardEntry

# ... (código existente)

@app.get("/groups/{group_id}/predictions/my")
def get_my_predictions_in_group(
    group_id: UUID,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    preds = session.exec(
        select(Prediction).where(
            Prediction.user_id == current_user.id,
            Prediction.group_id == group_id
        )
    ).all()
    
    # Calcular puntos en tiempo real para la vista del dashboard
    config = session.exec(select(GroupConfiguration).where(GroupConfiguration.group_id == group_id)).one()
    
    enriched_preds = []
    for p in preds:
        match = session.get(Match, p.match_id)
        points = 0
        if match and match.is_finished:
            is_ko = match.phase != "group"
            points = calculate_points(
                p.predicted_goals1, p.predicted_goals2,
                match.actual_goals1, match.actual_goals2,
                is_knockout=is_ko,
                pts_result=config.pts_result_ko if is_ko else config.pts_result_gr,
                pts_goals=config.pts_goals_ko if is_ko else config.pts_goals_gr,
                pts_diff=config.pts_diff_ko if is_ko else config.pts_diff_gr
            )
        
        enriched_preds.append({
            "match_id": p.match_id,
            "predicted_goals1": p.predicted_goals1,
            "predicted_goals2": p.predicted_goals2,
            "points_earned": points,
            "match_is_finished": match.is_finished if match else False,
            "actual_goals1": match.actual_goals1 if match else None,
            "actual_goals2": match.actual_goals2 if match else None
        })
        
    return enriched_preds

@app.get("/groups/{group_id}/matches/{match_id}/predictions")
def get_group_predictions_for_match(
    group_id: UUID,
    match_id: UUID,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    # 1. Verificar que el usuario pertenece al grupo
    member = session.exec(
        select(UserGroupLink).where(
            UserGroupLink.user_id == current_user.id,
            UserGroupLink.group_id == group_id
        )
    ).first()
    if not member:
        raise HTTPException(status_code=403, detail="No tienes acceso a este grupo")

    # 2. Verificar que el partido existe y está bloqueado
    match = session.get(Match, match_id)
    if not match:
        raise HTTPException(status_code=404, detail="Partido no encontrado")
    
    # Un partido se bloquea 5 minutos antes de empezar
    tz_gmt5 = timezone(timedelta(hours=-5))
    start_at_utc = match.start_at.replace(tzinfo=tz_gmt5).astimezone(timezone.utc)
    now_utc = datetime.now(timezone.utc)
    is_locked = (start_at_utc - now_utc).total_seconds() / 60 < 5
    
    if not is_locked and not match.is_finished:
        raise HTTPException(status_code=403, detail="Los pronósticos aún no son públicos para este partido")

    # 3. Obtener todos los pronósticos del grupo para este partido
    results = session.exec(
        select(Prediction, User.username)
        .join(User, Prediction.user_id == User.id)
        .where(
            Prediction.group_id == group_id,
            Prediction.match_id == match_id
        )
    ).all()

    return [
        {
            "username": username, 
            "predicted_goals1": p.predicted_goals1, 
            "predicted_goals2": p.predicted_goals2
        } 
        for p, username in results
    ]

@app.post("/predictions/bulk")
def create_bulk_predictions(
    predictions_data: List[dict], 
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    for item in predictions_data:
        match_id = uuid.UUID(item["match_id"])
        group_id = uuid.UUID(item["group_id"])
        
        # REGLA DE BLOQUEO CRÍTICA: Verificar hora GMT-5 (Colombia/Ecuador)
        match = session.get(Match, match_id)
        if not match:
            continue
            
        # El fixture está en GMT-5, convertimos las horas a UTC para comparar de forma estándar y segura
        tz_gmt5 = timezone(timedelta(hours=-5))
        match_start_utc = match.start_at.replace(tzinfo=tz_gmt5).astimezone(timezone.utc)
        now_utc = datetime.now(timezone.utc)
        time_diff = match_start_utc - now_utc
        
        if time_diff.total_seconds() < 300: # 5 minutos = 300 segundos
            # Si falta menos de 5 min o ya empezó, ignoramos este item
            continue
        
        # Buscar si ya existe para este usuario, partido Y grupo
        existing_prediction = session.exec(
            select(Prediction).where(
                Prediction.user_id == current_user.id,
                Prediction.match_id == match_id,
                Prediction.group_id == group_id
            )
        ).first()

        if existing_prediction:
            existing_prediction.predicted_goals1 = item["predicted_goals1"]
            existing_prediction.predicted_goals2 = item["predicted_goals2"]
            existing_prediction.updated_at = datetime.utcnow()
            session.add(existing_prediction)
        else:
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

@app.get("/groups/{group_id}/leaderboard", response_model=LeaderboardRead)
def get_group_leaderboard(
    group_id: UUID,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    # 1. Verificar acceso al grupo
    group = session.get(Group, group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Grupo no encontrado")
        
    member = session.exec(select(UserGroupLink).where(UserGroupLink.user_id == current_user.id, UserGroupLink.group_id == group_id)).first()
    if not member:
        raise HTTPException(status_code=403, detail="No tienes acceso a este grupo")
    
    # 2. Obtener configuración del grupo y partidos finalizados
    config = session.exec(select(GroupConfiguration).where(GroupConfiguration.group_id == group_id)).one()
    finished_matches = session.exec(select(Match).where(Match.is_finished == True)).all()
    
    leaderboard = []
    
    # 3. Calcular puntos por cada miembro (esto podría optimizarse en producción)
    # Obtenemos todos los miembros del grupo
    members = session.exec(
        select(User).join(UserGroupLink).where(UserGroupLink.group_id == group_id)
    ).all()
    
    for user in members:
        total_pts = 0
        exact_count = 0
        preds = session.exec(select(Prediction).where(Prediction.user_id == user.id, Prediction.group_id == group_id)).all()
        
        for p in preds:
            # Solo sumar puntos si el partido terminó
            m = next((m for m in finished_matches if m.id == p.match_id), None)
            if m:
                is_ko = m.phase != "group"
                pts = calculate_points(
                    p.predicted_goals1, p.predicted_goals2,
                    m.actual_goals1, m.actual_goals2,
                    is_knockout=is_ko,
                    pts_result=config.pts_result_ko if is_ko else config.pts_result_gr,
                    pts_goals=config.pts_goals_ko if is_ko else config.pts_goals_gr,
                    pts_diff=config.pts_diff_ko if is_ko else config.pts_diff_gr
                )
                total_pts += pts
                
                # Verificar si es marcador exacto
                if p.predicted_goals1 == m.actual_goals1 and p.predicted_goals2 == m.actual_goals2:
                    exact_count += 1
        
        leaderboard.append(LeaderboardEntry(
            user_id=user.id,
            username=user.username,
            full_name=user.full_name,
            avatar_url=user.avatar_url,
            total_points=total_pts,
            predictions_count=len(preds),
            exact_matches_count=exact_count
        ))
    
    # 4. Ordenar: Puntos desc, luego nombre
    leaderboard.sort(key=lambda x: (-x.total_points, x.username))
    
    return LeaderboardRead(group_id=group_id, entries=leaderboard)

from app.schemas.admin import MatchUpdateResult, MatchCreateAdmin

async def get_current_active_superuser(
    current_user: User = Depends(get_current_user),
) -> User:
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="No tienes permisos de administrador"
        )
    return current_user

@app.post("/admin/matches/{match_id}/results", response_model=MatchRead)
def update_match_result(
    match_id: UUID,
    result_data: MatchUpdateResult,
    session: Session = Depends(get_session),
    admin_user: User = Depends(get_current_active_superuser)
):
    match = session.get(Match, match_id)
    if not match:
        raise HTTPException(status_code=404, detail="Partido no encontrado")
    
    match.is_finished = result_data.is_finished
    if not result_data.is_finished:
        match.actual_goals1 = None
        match.actual_goals2 = None
    else:
        match.actual_goals1 = result_data.actual_goals1
        match.actual_goals2 = result_data.actual_goals2
    
    session.add(match)
    session.commit()
    session.refresh(match)
    return map_match_to_read(match)

@app.post("/admin/matches", response_model=MatchRead)
def create_match_admin(
    match_data: MatchCreateAdmin,
    session: Session = Depends(get_session),
    admin_user: User = Depends(get_current_active_superuser)
):
    new_match = Match(
        team1=match_data.team1,
        team2=match_data.team2,
        group_name=match_data.group_name,
        stadium=match_data.stadium,
        start_at=match_data.start_at,
        phase=match_data.phase
    )
    session.add(new_match)
    session.commit()
    session.refresh(new_match)
    return map_match_to_read(new_match)

@app.get("/test-scoring")
def test_scoring(p1: int, p2: int, a1: int, a2: int, knockout: bool = False):
    pts = calculate_points(p1, p2, a1, a2, knockout)
    return {"points": pts}
