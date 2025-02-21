# To run: uvicorn main:app --reload 
from fastapi import FastAPI, Request, Form, Depends
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from database import SessionLocal, Project, Task

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Dependency to get a database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Main page: Display everything
@app.get("/")
def home(request: Request, db: Session = Depends(get_db)):
    projects = db.query(Project).all()
    tasks = db.query(Task).order_by(Task.priority).all()
    
    # Prepare data for visualization
    nodes = []
    edges = []
    for p in projects:
        nodes.append({"id": p.id, "label": p.name, "group": "project"})
        for t in p.tasks:
            nodes.append({"id": t.id + 1000, "label": t.name, "group": "task"})
            edges.append({"from": p.id, "to": t.id + 1000})
    
    return templates.TemplateResponse("index.html", {
        "request": request,
        "projects": projects,
        "tasks": tasks,
        "nodes": nodes,
        "edges": edges,
        "message": None
    })

# Add project
@app.post("/add_project")
def add_project(request: Request, name: str = Form(...), db: Session = Depends(get_db)):
    project = Project(name=name)
    db.add(project)
    db.commit()
    
    projects = db.query(Project).all()
    tasks = db.query(Task).order_by(Task.priority).all()
    nodes, edges = generate_vis_data(projects)
    return templates.TemplateResponse("index.html", {
        "request": request,
        "projects": projects,
        "tasks": tasks,
        "nodes": nodes,
        "edges": edges,
        "message": "Project added successfully"
    })

# Add task
@app.post("/add_task")
def add_task(
    request: Request, 
    project_id: int = Form(...), 
    name: str = Form(...), 
    priority: str = Form(...), 
    learning: bool = Form(False), 
    db: Session = Depends(get_db)
):
    task = Task(name=name, priority=priority, learning=learning, project_id=project_id)
    db.add(task)
    db.commit()
    
    projects = db.query(Project).all()
    tasks = db.query(Task).order_by(Task.priority).all()
    nodes, edges = generate_vis_data(projects)
    return templates.TemplateResponse("index.html", {
        "request": request,
        "projects": projects,
        "tasks": tasks,
        "nodes": nodes,
        "edges": edges,
        "message": "Task added successfully"
    })
@app.post("/toggle_complete")
def toggle_complete(request: Request, task_id: int = Form(...), completed: str = Form(None), db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if task:
        task.completed = completed == "true"  # Set to True if checkbox is checked, False otherwise
        db.commit()
    return RedirectResponse(url="/", status_code=303)

# Helper function to generate visualization data
def generate_vis_data(projects):
    nodes = []
    edges = []
    for p in projects:
        nodes.append({"id": p.id, "label": p.name, "group": "project"})
        for t in p.tasks:
            nodes.append({"id": t.id + 1000, "label": t.name, "group": "task"})
            edges.append({"from": p.id, "to": t.id + 1000})
    return nodes, edges