from flask import Flask
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlite3
from typing import List, Optional

app = FastAPI(title="To-Do Service")


# Модель для задачи
class Item(BaseModel):
    id: Optional[int] = None  # Необязательное поле для ID
    title: str
    description: Optional[str] = None
    completed: bool = False

# Создание таблицы при старте приложения
def init_db():
    with sqlite3.connect("tasks.db") as conn:
        cur = conn.cursor()
        cur.execute("""
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            completed BOOLEAN NOT NULL DEFAULT 0
        )
        """)
        conn.commit()

init_db()

# Эндпоинты ToDo-сервиса
@app.post("/items", response_model=Item)
def create_item(item: Item):
    with sqlite3.connect("tasks.db") as conn:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO items (title, description, completed) VALUES (?, ?, ?)",
            (item.title, item.description, item.completed)
        )
        conn.commit()
        item.id = cur.lastrowid
    return item

@app.get("/items", response_model=List[Item])
def read_items():
    with sqlite3.connect("tasks.db") as conn:
        cur = conn.cursor()
        cur.execute("SELECT id, title, description, completed FROM items")
        rows = cur.fetchall()
    return [{"id": row[0], "title": row[1], "description": row[2], "completed": bool(row[3])} for row in rows]

@app.get("/items/{item_id}", response_model=Item)
def read_item(item_id: int):
    with sqlite3.connect("tasks.db") as conn:
        cur = conn.cursor()
        cur.execute("SELECT id, title, description, completed FROM items WHERE id = ?", (item_id,))
        row = cur.fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"id": row[0], "title": row[1], "description": row[2], "completed": bool(row[3])}

@app.put("/items/{item_id}", response_model=Item)
def update_item(item_id: int, item: Item):
    with sqlite3.connect("tasks.db") as conn:
        cur = conn.cursor()
        cur.execute("UPDATE items SET title = ?, description = ?, completed = ? WHERE id = ?", 
                    (item.title, item.description, item.completed, item_id))
        conn.commit()
        
        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="Item not found")
    
    item.id = item_id
    return item

@app.delete("/items/{item_id}")
def delete_item(item_id: int):
    with sqlite3.connect("tasks.db") as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM items WHERE id = ?", (item_id,))
        conn.commit()
        
        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="Item not found")
    
    return {"detail": "Item deleted successfully"}
