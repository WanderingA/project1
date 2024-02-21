"""
包含数据库连接和会话的配置。
"""
from sqlalchemy import create_engine, Column, Integer, String, Boolean, Double, DateTime, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
import os
from dotenv import load_dotenv


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# print(BASE_DIR)
load_dotenv(os.path.join(BASE_DIR, ".env"))
DATABASE_URL = os.getenv('DATABASE_URL')
# print(DATABASE_URL)
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(30), unique=True, index=True)
    hashed_password = Column(String(100))
    is_admin = Column(Boolean, default=False)


class Nodes(Base):
    __tablename__ = "nodes"

    id = Column(Integer, primary_key=True, index=True)
    node_id = Column(Integer, unique=True, index=True)
    seismic_state = Column(String(30), index=True)
    longitude = Column(Double, index=True)
    latitude = Column(Double, index=True)
    energy = Column(Double, index=True)
    space = Column(Double, index=True)
    gps_state = Column(String(30), index=True)
    detector_state = Column(String(30), index=True)
    angle = Column(String(30), index=True)
    timestamp = Column(DateTime, index=True)

    data = relationship("Data", back_populates="node")
    classification = relationship("Classification", back_populates="node")
    rock = relationship("Rock", back_populates="node")


class Data(Base):
    __tablename__ = "data"

    id = Column(Integer, primary_key=True, index=True)
    node_id = Column(Integer, ForeignKey('nodes.node_id'), index=True)
    timestamp = Column(DateTime, index=True)
    sample_rate = Column(Integer, index=True)
    sample_length = Column(Integer, index=True)
    file = Column(String(120), index=True)

    node = relationship("Nodes", back_populates="data")


class Classification(Base):
    __tablename__ = "classification"

    id = Column(Integer, primary_key=True, index=True)
    node_id = Column(Integer, ForeignKey('nodes.node_id'), index=True)
    timestamp = Column(DateTime, index=True)
    classification = Column(String(30), index=True)

    node = relationship("Nodes", back_populates="classification")


class Rock(Base):
    __tablename__ = "rock"

    id = Column(Integer, primary_key=True, index=True)
    node_id = Column(Integer, ForeignKey('nodes.node_id'), index=True)
    timestamp = Column(DateTime, index=True)
    rock = Column(String(30), index=True)

    node = relationship("Nodes", back_populates="rock")


# 如果表不存在，则创建表
Base.metadata.create_all(bind=engine)
