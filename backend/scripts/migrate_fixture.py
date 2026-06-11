import os
import pandas as pd
from datetime import datetime
from sqlmodel import Session, create_engine, select
from app.models.models import Match, SQLModel

# Cargar variables de entorno si existen, o usar una local para pruebas
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")
engine = create_engine(DATABASE_URL)

def migrate_fixture():
    # Crear tablas si no existen (útil para el paso 1 local)
    SQLModel.metadata.create_all(engine)
    
    file_path = "../fifa_world_cup_2026.xlsx"
    df = pd.read_excel(file_path, sheet_name="fixture")
    
    with Session(engine) as session:
        for _, row in df.iterrows():
            # Combinar fecha y hora
            # Manejar si row["time"] es datetime o time
            match_time = row["time"]
            if isinstance(match_time, datetime):
                match_time = match_time.time()
            
            start_at = datetime.combine(row["date"].date(), match_time)
            
            match = Match(
                team1=row["team1"],
                team2=row["team2"],
                group_name=row["group"],
                stadium=row["stadium"],
                start_at=start_at,
                phase="group"
            )
            session.add(match)
        
        session.commit()
        print(f"Se han migrado {len(df)} partidos exitosamente.")

if __name__ == "__main__":
    migrate_fixture()
