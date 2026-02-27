from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base
from datetime import datetime, timezone
import logging

# SQLite database file will be created automatically in project folder
DATABASE_URL = "sqlite:///./financial_analyzer.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}  # Needed for SQLite with FastAPI
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


# Database model — one row per analysis
class AnalysisResult(Base):
    __tablename__ = "analysis_results"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    query = Column(Text, nullable=False)
    analysis = Column(Text, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


def init_db():
    """Create tables if they don't exist"""
    Base.metadata.create_all(bind=engine)


def save_result(filename: str, query: str, analysis: str):
    """Save an analysis result to the database"""
    db = SessionLocal()
    try:
        result = AnalysisResult(
            filename=filename,
            query=query,
            analysis=analysis
        )
        db.add(result)
        db.commit()
        db.refresh(result)
        return result
    except Exception:
        logging.exception("Failed to save analysis result")
        db.rollback()
        raise
    finally:
        db.close()


def get_all_results():
    """Retrieve all saved analysis results"""
    db = SessionLocal()
    try:
        return db.query(AnalysisResult).order_by(AnalysisResult.created_at.desc()).all()
    finally:
        db.close()


def get_result_by_id(result_id: int):
    """Retrieve a single analysis result by ID"""
    db = SessionLocal()
    try:
        return db.query(AnalysisResult).filter(AnalysisResult.id == result_id).first()
    finally:
        db.close()
