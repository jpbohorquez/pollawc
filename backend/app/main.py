from fastapi import FastAPI, Depends, HTTPException, status
from sqlmodel import Session, create_engine, select
from app.models.models import Match, Group, Prediction, User, SQLModel
from app.services.scoring import calculate_points
from typing import List
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")
engine = create_engine(DATABASE_URL)

def get_session():
    with Session(engine) as session:
        yield session

app = FastAPI(title="Gol Predictor API")

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
