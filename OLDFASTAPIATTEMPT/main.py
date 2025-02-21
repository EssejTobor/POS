# To run: uvicorn main:app --reload 
from fastapi import FastAPI, Form, Depends, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session, joinedload
from database import Goal, Subgoal, Task, Subtask, get_db

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Generate data for vis.js visualization
def generate_vis_data(goals):
    nodes = []
    edges = []

    for goal in goals:
        goal_id = goal.id
        nodes.append({"id": goal_id, "label": goal.title, "group": "goal", "color": "blue"})
        for subgoal in goal.subgoals:
            subgoal_id = subgoal.id + 1000
            nodes.append({"id": subgoal_id, "label": subgoal.title, "group": "subgoal", "color": "lightblue"})
            edges.append({"from": goal_id, "to": subgoal_id})
            for task in subgoal.tasks:
                task_id = task.id + 2000
                task_color = "green" if task.completed else "red"
                nodes.append({"id": task_id, "label": f"Task: {task.title}", "group": "task", "color": task_color})
                edges.append({"from": subgoal_id, "to": task_id})
                for subtask in task.subtasks:
                    subtask_id = subtask.id + 3000
                    subtask_color = "green" if subtask.completed else "red"
                    nodes.append({"id": subtask_id, "label": f"Sub-Task: {subtask.title}", "group": "subtask", "color": subtask_color})
                    edges.append({"from": task_id, "to": subtask_id})

    return nodes, edges

# Home page
@app.get("/")
def home(request: Request, db: Session = Depends(get_db)):
    goals = db.query(Goal).options(
        joinedload(Goal.subgoals).joinedload(Subgoal.tasks).joinedload(Task.subtasks)
    ).all()
    nodes, edges = generate_vis_data(goals)
    return templates.TemplateResponse("index.html", {
        "request": request,
        "goals": goals,
        "nodes": nodes,
        "edges": edges
    })

# Add goal
@app.post("/add_goal")
def add_goal(
    title: str = Form(...),
    time_horizon: str = Form(...),
    rationale: str = Form(...),
    key_metrics: str = Form(...),
    db: Session = Depends(get_db)
):
    goal = Goal(
        title=title,
        time_horizon=time_horizon,
        rationale=rationale,
        key_metrics=key_metrics
    )
    db.add(goal)
    db.commit()
    return RedirectResponse(url="/", status_code=303)

# Add subgoal
@app.post("/add_subgoal")
def add_subgoal(
    goal_id: int = Form(...),
    title: str = Form(...),
    time_horizon: str = Form(...),
    rationale: str = Form(...),
    key_metrics: str = Form(...),
    db: Session = Depends(get_db)
):
    subgoal = Subgoal(
        title=title,
        time_horizon=time_horizon,
        rationale=rationale,
        key_metrics=key_metrics,
        goal_id=goal_id
    )
    db.add(subgoal)
    db.commit()
    return RedirectResponse(url="/", status_code=303)

# Add task
@app.post("/add_task")
def add_task(
    subgoal_id: int = Form(...),
    title: str = Form(...),
    db: Session = Depends(get_db)
):
    task = Task(
        title=title,
        subgoal_id=subgoal_id
    )
    db.add(task)
    db.commit()
    return RedirectResponse(url="/", status_code=303)

# Add subtask
@app.post("/add_subtask")
def add_subtask(
    task_id: int = Form(...),
    title: str = Form(...),
    db: Session = Depends(get_db)
):
    subtask = Subtask(
        title=title,
        task_id=task_id
    )
    db.add(subtask)
    db.commit()
    return RedirectResponse(url="/", status_code=303)

# Toggle completion
@app.post("/toggle_completion")
def toggle_completion(
    entity_type: str = Form(...),
    entity_id: int = Form(...),
    completed: str = Form(None),
    db: Session = Depends(get_db)
):
    if entity_type == "task":
        task = db.query(Task).filter(Task.id == entity_id).first()
        if task:
            task.completed = completed == "on"
            db.commit()
    elif entity_type == "subtask":
        subtask = db.query(Subtask).filter(Subtask.id == entity_id).first()
        if subtask:
            subtask.completed = completed == "on"
            db.commit()
    return RedirectResponse(url="/", status_code=303)