from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base



# SQLALCHEMY_DATABASE_URL = "postgresql://postgres.qksfcpqimmgarjtmhkwv:11212233232reon@aws-0-ap-southeast-1.pooler.supabase.com:5432/postgres"
import os


SQLALCHEMY_DATABASE_URL = os.getenv("postgresql://postgres.qksfcpqimmgarjtmhkwv:11212233232reon@aws-0-ap-southeast-1.pooler.supabase.com:5432/postgres")
# SQLALCHEMY_DATABASE_URL = 'sqlite:///./library.db'
engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autoflush=False, autocommit = False, bind = engine)


Base = declarative_base()