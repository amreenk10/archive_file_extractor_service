import os
import urllib.parse

class Config:

    SECRET_KEY=os.getenv("SECRET_KEY","secret-key-in-production")
    JWT_SECRET_KEY=os.getenv("JWT_SECRET_KEY","secure-jwt-token")

    CONCURRENCY= int(os.getenv("CONCURRENCY",4))
    DB_USER=os.getenv("DB_USER","postgres")
    raw_password =os.getenv("DB_PASSWORD","Amreenks10_$")
    DB_PASSWORD = urllib.parse.quote_plus(raw_password)
    DB_HOST=os.getenv("DB_HOST","localhost")
    DB_PORT=os.getenv("DB_PORT","5432")
    DB_NAME=os.getenv("DB_NAME","extractor")

    SQLALCHEMY_DATABASE_URI=f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

    SQLALCHEMY_TRACK_MODIFICATIONS=False