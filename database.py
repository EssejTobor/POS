from sqlalchemy import create_engine, Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship, declarative_base

# Set up the database
Base = declarative_base()
engine = create_engine('sqlite:///my_pos.db')
SessionLocal = sessionmaker(bind=engine)

# Define Project and Task structures
class Project(Base):
    __tablename__ = 'projects'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    tasks = relationship("Task", back_populates="project")

class Task(Base):
    __tablename__ = 'tasks'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    priority = Column(String)  # e.g., "high", "medium", "low"
    learning = Column(Boolean, default=False)  # Flag for learning tasks
    completed = Column(Boolean, default=False)
    project_id = Column(Integer, ForeignKey('projects.id'))
    project = relationship("Project", back_populates="tasks")

# Create the tables if they don’t exist
Base.metadata.create_all(engine)