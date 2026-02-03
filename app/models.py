from datetime import datetime, date
from sqlalchemy import DateTime, Date, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db import Base


class Meeting(Base):
    __tablename__ = "meetings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(200))
    meeting_date: Mapped[date] = mapped_column(Date)
    timezone: Mapped[str] = mapped_column(String(100))
    gemini_notes: Mapped[str] = mapped_column(Text)
    transcript: Mapped[str | None] = mapped_column(Text, nullable=True)
    summary: Mapped[str] = mapped_column(Text)
    decisions: Mapped[str] = mapped_column(Text)
    risks_blockers: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    tasks: Mapped[list["Task"]] = relationship(
        "Task", back_populates="meeting", cascade="all, delete-orphan"
    )


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    meeting_id: Mapped[int] = mapped_column(ForeignKey("meetings.id"))
    title: Mapped[str] = mapped_column(String(250))
    project: Mapped[str | None] = mapped_column(String(200), nullable=True)
    due_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    due_date_confidence: Mapped[float] = mapped_column(Float)
    priority: Mapped[str] = mapped_column(String(20))
    status: Mapped[str] = mapped_column(String(20), default="proposed")
    confidence: Mapped[float] = mapped_column(Float)
    source_type: Mapped[str] = mapped_column(String(20))
    source_quote: Mapped[str] = mapped_column(Text)
    tags: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    meeting: Mapped[Meeting] = relationship("Meeting", back_populates="tasks")
