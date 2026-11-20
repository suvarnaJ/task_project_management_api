import os
from datetime import datetime, timezone
from typing import Optional

from bson import ObjectId
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field
from pymongo import MongoClient, ASCENDING

MONGODB_URL = os.getenv("MONGODB_URL", "")
if not MONGODB_URL:
    raise RuntimeError("Set MONGODB_URL in your environment or .env file.")

client = MongoClient(MONGODB_URL, serverSelectionTimeoutMS=5000)
db = client[os.getenv("MONGODB_DATABASE", "task_management")]
projects = db["projects"]
tasks = db["tasks"]

# Useful indexes for common filters and project lookups.
tasks.create_index([("project_id", ASCENDING)])
tasks.create_index([("status", ASCENDING)])
tasks.create_index([("assignee", ASCENDING)])


def to_id(value: str) -> ObjectId:
    if not ObjectId.is_valid(value):
        raise HTTPException(status_code=400, detail="Invalid ID")
    return ObjectId(value)


def serialize_project(doc: dict) -> dict:
    return {
        "id": str(doc["_id"]),
        "name": doc["name"],
        "description": doc.get("description"),
        "created_at": doc["created_at"],
    }


def serialize_task(doc: dict) -> dict:
    return {
        "id": str(doc["_id"]),
        "project_id": str(doc["project_id"]),
        "title": doc["title"],
        "description": doc.get("description"),
        "assignee": doc.get("assignee"),
        "status": doc.get("status", "TODO"),
        "created_at": doc["created_at"],
    }


class ProjectCreate(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    description: Optional[str] = None


class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = None


class AssignRequest(BaseModel):
    assignee: str = Field(min_length=1, max_length=120)


class StatusRequest(BaseModel):
    status: str = Field(pattern="^(TODO|IN_PROGRESS|DONE|BLOCKED)$")


app = FastAPI(title="Task Management API - MongoDB", version="1.0.0")


@app.get("/")
def root():
    return {"message": "Task Management API - MongoDB", "docs": "/docs"}


@app.get("/health")
def health():
    client.admin.command("ping")
    return {"database": "connected"}


@app.post("/projects", status_code=status.HTTP_201_CREATED)
def create_project(payload: ProjectCreate):
    document = {
        **payload.model_dump(),
        "created_at": datetime.now(timezone.utc),
    }
    result = projects.insert_one(document)
    document["_id"] = result.inserted_id
    return serialize_project(document)


@app.get("/projects")
def list_projects():
    return [serialize_project(doc) for doc in projects.find().sort("_id", ASCENDING)]


@app.post("/projects/{project_id}/tasks", status_code=status.HTTP_201_CREATED)
def create_task(project_id: str, payload: TaskCreate):
    project_oid = to_id(project_id)
    if not projects.find_one({"_id": project_oid}):
        raise HTTPException(status_code=404, detail="Project not found")
    document = {
        "project_id": project_oid,
        **payload.model_dump(),
        "assignee": None,
        "status": "TODO",
        "created_at": datetime.now(timezone.utc),
    }
    result = tasks.insert_one(document)
    document["_id"] = result.inserted_id
    return serialize_task(document)


@app.patch("/tasks/{task_id}/assign")
def assign_task(task_id: str, payload: AssignRequest):
    result = tasks.find_one_and_update(
        {"_id": to_id(task_id)},
        {"$set": {"assignee": payload.assignee}},
        return_document=True,
    )
    if not result:
        raise HTTPException(status_code=404, detail="Task not found")
    return serialize_task(result)


@app.patch("/tasks/{task_id}/status")
def update_status(task_id: str, payload: StatusRequest):
    result = tasks.find_one_and_update(
        {"_id": to_id(task_id)},
        {"$set": {"status": payload.status}},
        return_document=True,
    )
    if not result:
        raise HTTPException(status_code=404, detail="Task not found")
    return serialize_task(result)


@app.get("/tasks")
def get_tasks(
    project_id: Optional[str] = None,
    status_filter: Optional[str] = None,
    assignee: Optional[str] = None,
):
    query = {}
    if project_id:
        query["project_id"] = to_id(project_id)
    if status_filter:
        query["status"] = status_filter.upper()
    if assignee:
        query["assignee"] = assignee
    return [serialize_task(doc) for doc in tasks.find(query).sort("_id", ASCENDING)]


@app.get("/tasks/{task_id}")
def get_task(task_id: str):
    doc = tasks.find_one({"_id": to_id(task_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Task not found")
    return serialize_task(doc)


@app.delete("/tasks/{task_id}")
def delete_task(task_id: str):
    result = tasks.delete_one({"_id": to_id(task_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"message": "Task deleted", "task_id": task_id}
