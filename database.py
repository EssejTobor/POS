from sqlalchemy import create_engine, Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship, declarative_base


# Set up the database
Base = declarative_base()
engine = create_engine('sqlite:///my_pos.db')
SessionLocal = sessionmaker(bind=engine)

# Define models
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
    learning = Column(Boolean, default=False)
    completed = Column(Boolean, default=False)
    project_id = Column(Integer, ForeignKey('projects.id'))
    parent_id = Column(Integer, ForeignKey('tasks.id'), nullable=True)  # For sub-tasks
    project = relationship("Project", back_populates="tasks")
    parent = relationship("Task", remote_side=[id], backref="subtasks")  # Self-referential

# Create tables
Base.metadata.create_all(engine)