from sqlalchemy import create_engine, Integer, Column, String, create_mock_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from fastapi import APIRouter, Depends, HTTPException
import os
from dotenv import load_dotenv
from app.utils.wordcloud.wordcloud_functions import complexity_df


load_dotenv()

router = APIRouter()


# connect to ElephantSQL-hosted PostgreSQL
DB_NAME = os.getenv("RDS_DB_NAME", default=None)
DB_USER = os.getenv("RDS_USERNAME", default=None)
DB_PASSWORD = os.getenv("RDS_PASSWORD", default=None)
DB_HOST = os.getenv("RDS_HOSTNAME", default=None)
DB_PORT = os.getenv("RDS_PORT", default=None)


def dump(sql, *multiparams, **params):
    print(sql.compile(dialect=engine.dialect))

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = None
if all([DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT]):
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)
else:
    print("Warning: Not all RDS environment variables set, falling back to mock database")
    engine = create_mock_engine("postgresql://mock:{mock}@mock:5432/mock", dump)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

Base.metadata.create_all(bind=engine)


class Stories(Base):
    __tablename__ = "stories"

    id = Column(Integer, primary_key=True, index=True)
    story = Column(String, index=True)


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


def get_story(db: Session, id: int):
    return db.query(Stories).filter(Stories.id == id).first()


@router.get("/storytext")
def show_story(id: int = 1, numWords: int = 20, db: Session = Depends(get_db)):
    db_story = get_story(db, id=id)
    if db_story is None:
        raise HTTPException(
            status_code=404, detail="Story not found, id must be between 1-167"
        )

    story_string = db_story.story

    # sends the string of the story and the number of words we want the complexity for
    words = complexity_df(story_string, numWords)

    return words

