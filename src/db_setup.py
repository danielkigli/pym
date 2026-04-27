import os
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime

Base = declarative_base()


class ReportInsight(Base):
    """
    SQLAlchemy Model representing the extracted information from a Maya report.
    """

    __tablename__ = "report_insights"

    id = Column(Integer, primary_key=True, autoincrement=True)
    report_url = Column(String, unique=True, nullable=False)
    company_name = Column(String, nullable=True)
    person_name = Column(String, nullable=True)
    job_title = Column(String, nullable=True)
    action = Column(String, nullable=True)  # e.g. "BUY", "SELL"
    amount_shares = Column(Float, nullable=True)
    price_per_share = Column(Float, nullable=True)
    report_date = Column(DateTime, default=datetime.utcnow)
    raw_text = Column(Text, nullable=True)


def get_engine():
    # Defaults to a local postgres database named tase_db
    # Example format: postgresql://postgres:mysecretpassword@localhost:5432/tase_db
    db_url = os.environ.get(
        "DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/tase_db"
    )
    return create_engine(db_url)


def init_db():
    engine = get_engine()
    # Create all tables in the engine. This is equivalent to "Create Table" statements in raw SQL.
    Base.metadata.create_all(engine)
    print("Database tables initialized successfully.")


def get_session():
    engine = get_engine()
    Session = sessionmaker(bind=engine)
    return Session()


if __name__ == "__main__":
    init_db()
