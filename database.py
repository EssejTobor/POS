from sqlalchemy import create_engine, Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

Base = declarative_base()

class Goal(Base):
    __tablename__ = "goals"
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    time_horizon = Column(String, nullable=False)
    rationale = Column(String, nullable=False)
    key_metrics = Column(String, nullable=False)  # Metrics separated by newlines
    subgoals = relationship("Subgoal", back_populates="goal")

class Subgoal(Base):
    __tablename__ = "subgoals"
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    time_horizon = Column(String, nullable=False)
    rationale = Column(String, nullable=False)
    key_metrics = Column(String, nullable=False)
    goal_id = Column(Integer, ForeignKey("goals.id"), nullable=False)
    goal = relationship("Goal", back_populates="subgoals")
    tasks = relationship("Task", back_populates="subgoal")

class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    completed = Column(Boolean, default=False)
    subgoal_id = Column(Integer, ForeignKey("subgoals.id"), nullable=False)
    subgoal = relationship("Subgoal", back_populates="tasks")
    subtasks = relationship("Subtask", back_populates="task")

class Subtask(Base):
    __tablename__ = "subtasks"
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    completed = Column(Boolean, default=False)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    task = relationship("Task", back_populates="subtasks")

# Set up the database
engine = create_engine("sqlite:///project.db")
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

def get_db():
    db = Session()
    try:
        yield db
    finally:
        db.close()