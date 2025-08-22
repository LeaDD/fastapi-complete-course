# # Instructor model

# from database import Base
# from sqlalchemy import Column, Integer, String, Boolean

# class Todos(Base):
#     __tablename__="todos"
#     id = Column(Integer, primary_key=True, index=True)
#     title = Column(String)
#     description = Column(String)
#     priority = Column(Integer)
#     complete = Column(Boolean, default=False)

# Newer more modern approach - also this is consistent with how I am doing it in my personal site
from sqlalchemy.orm import Mapped, mapped_column
from database import Base

class Todos(Base):
    __tablename__ = "todos"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column()
    description: Mapped[str] = mapped_column()
    priority: Mapped[int] = mapped_column()
    complete: Mapped[bool] = mapped_column(default=False)


