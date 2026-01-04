from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlite3
import hashlib

app = FastAPI(title="URL Shortener Service")

# Модель для сокращения URL
class URL(BaseModel):
    url: str

# Создание таблицы при старте приложения
def init_db():
    with sqlite3.connect("urls.db") as conn:
        cur = conn.cursor()
        cur.execute("""
        CREATE TABLE IF NOT EXISTS urls (
            short_id TEXT PRIMARY KEY,
            full_url TEXT NOT NULL
        )
        """)
        conn.commit()

init_db()

# Эндпоинты сервиса сокращения URL
@app.post("/shorten")
def shorten_url(url: URL):
    short_id = hashlib.md5(url.url.encode()).hexdigest()[:6]  # Генерация короткого ID (6 символов)
    
    with sqlite3.connect("urls.db") as conn:
        cur = conn.cursor()
        cur.execute("INSERT INTO urls (short_id, full_url) VALUES (?, ?)", (short_id, url.url))
        conn.commit()
    
    return {"short_url": f"http://localhost:8001/{short_id}"}

@app.get("/{short_id}")
def redirect_to_full_url(short_id: str):
    with sqlite3.connect("urls.db") as conn:
        cur = conn.cursor()
        cur.execute("SELECT full_url FROM urls WHERE short_id = ?", (short_id,))
        row = cur.fetchone()
    
    if row is None:
        raise HTTPException(status_code=404, detail="Short URL not found")
    
    return {"full_url": row[0]}

@app.get("/stats/{short_id}")
def get_url_stats(short_id: str):
    with sqlite3.connect("urls.db") as conn:
        cur = conn.cursor()
        cur.execute("SELECT full_url FROM urls WHERE short_id = ?", (short_id,))
        row = cur.fetchone()
    
    if row is None:
        raise HTTPException(status_code=404, detail="Short URL not found")
    
    return {"short_id": short_id, "full_url": row[0]}