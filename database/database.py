from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from schemas import settings
import redis

redis_client=redis.Redis.from_url(settings.REDIS_URL,decode_responses=True)
engine = create_engine(settings.DATABASE_URL)
SessionLocal=sessionmaker(autocommit=False,autoflush=False,bind=engine)
Base=declarative_base()

def get_redis():
    return redis_client

def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()    