# main/dbmodels.py
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
from passlib.hash import sha256_crypt

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    is_admin = Column(Boolean, default=False)
    must_reset = Column(Boolean, default=True)
    temp_expiry = Column(DateTime, default=datetime.utcnow)

# SQLite setup
DATABASE_URL = "sqlite:///./users.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)
    
    # Auto-create admin user if none exists
    db = SessionLocal()
    try:
        if not db.query(User).filter(User.is_admin == True).first():
            admin = User(
                email="admin@admin.com",
                password_hash=sha256_crypt.hash("admin"),
                is_admin=True,
                must_reset=False,
                temp_expiry=datetime.utcnow() + timedelta(days=365)
            )
            db.add(admin)
            db.commit()
            print("Admin user created automatically!")
    except Exception as e:
        print(f"Error creating admin user: {e}")
        db.rollback()
    finally:
        db.close()