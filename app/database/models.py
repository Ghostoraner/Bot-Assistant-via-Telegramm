from datetime import datetime
from sqlalchemy import BigInteger, String, Boolean, ForeignKey, DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'users'


    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=False)
    language: Mapped[str] = mapped_column(String(2), default="ru", nullable=False)
    notifications: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    search_category: Mapped[str] = mapped_column(String(50), default="all", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class Task(Base):
    __tablename__ = 'tasks'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False)
    is_good: Mapped[bool] = mapped_column(Boolean, nullable=True)


class Planer(Base):
    __tablename__ = 'planers'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    due_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)