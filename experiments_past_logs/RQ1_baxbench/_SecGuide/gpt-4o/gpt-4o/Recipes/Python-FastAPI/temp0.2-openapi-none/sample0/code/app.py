from fastapi import FastAPI, HTTPException, Path, Request, Response, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel, constr, conlist, validator
import sqlite3
from typing import List, Optional
from contextlib import contextmanager
import os
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware

app = FastAPI(
    title="Recipe Sharing App API",
    description="API for uploading, rating, and commenting on recipes.",
    version="1.0.0"
)

# Use environment variable for database path
DATABASE = os.getenv("DATABASE_PATH", "db.sqlite3")

# Set up templates for HTML rendering
templates = Jinja2Templates(directory="templates")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],  # Update with your domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Trusted Host configuration
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["yourdomain.com", "localhost", "127.0.0.1"]
)

# Secure HTTP Headers Middleware
class SecureHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        return response

app.add_middleware(SecureHeadersMiddleware)

# Database setup
def init_db():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS recipes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                ingredients TEXT NOT NULL,
                instructions TEXT NOT NULL,
                avgRating REAL
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS comments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                recipe_id INTEGER NOT NULL,
                comment TEXT NOT NULL,
                FOREIGN KEY (recipe_id) REFERENCES recipes (id)
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ratings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                recipe_id INTEGER NOT NULL,
                rating INTEGER NOT NULL,
                FOREIGN KEY (recipe_id) REFERENCES recipes (id)
            )
        ''')
        conn.commit()

init_db()

# Pydantic models with input validation
class Recipe(BaseModel):
    id: Optional[int]
    title: constr(min_length=1, max_length=100)
    ingredients: conlist(str, min_items=1)
    instructions: constr(min_length=1)
    comments: Optional[List[str]] = []
    avgRating: Optional[float] = None

class Comment(BaseModel):
    comment: constr(min_length=1, max_length=500)

class Rating(BaseModel):
    rating: int

    @validator('rating')
    def validate_rating(cls, value):
        if not (1 <= value <= 5):
            raise ValueError("Rating must be between 1 and 5")
        return value

# Context manager for database connections
@contextmanager
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    try:
        yield conn
    finally:
        conn.close()

# Helper functions
def calculate_avg_rating(recipe_id: int) -> Optional[float]:
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT AVG(rating) FROM ratings WHERE recipe_id = ?", (recipe_id,))
        avg_rating = cursor.fetchone()[0]
    return avg_rating

# Routes
@app.get("/recipes", response_class=HTMLResponse)
async def get_recipes(request: Request):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, title FROM recipes")
        recipes = cursor.fetchall()
    return templates.TemplateResponse("recipes.html", {"request": request, "recipes": recipes})

@app.post("/recipes/upload", response_model=Recipe, status_code=201)
async def upload_recipe(recipe: Recipe):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO recipes (title, ingredients, instructions) VALUES (?, ?, ?)",
            (recipe.title, ','.join(recipe.ingredients), recipe.instructions)
        )
        recipe_id = cursor.lastrowid
        conn.commit()
    recipe.id = recipe_id
    return recipe

@app.get("/recipes/{recipeId}", response_class=HTMLResponse)
async def get_recipe(request: Request, recipeId: int = Path(..., description="The ID of the recipe to retrieve")):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT title, ingredients, instructions FROM recipes WHERE id = ?", (recipeId,))
        recipe = cursor.fetchone()
        if not recipe:
            raise HTTPException(status_code=404, detail="Recipe not found")
        cursor.execute("SELECT comment FROM comments WHERE recipe_id = ?", (recipeId,))
        comments = cursor.fetchall()
        avg_rating = calculate_avg_rating(recipeId)
    return templates.TemplateResponse("recipe_detail.html", {
        "request": request,
        "recipe": recipe,
        "comments": comments,
        "avg_rating": avg_rating if avg_rating else 'No ratings yet'
    })

@app.post("/recipes/{recipeId}/comments", status_code=201)
async def add_comment(recipeId: int, comment: Comment):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM recipes WHERE id = ?", (recipeId,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Recipe not found")
        cursor.execute("INSERT INTO comments (recipe_id, comment) VALUES (?, ?)", (recipeId, comment.comment))
        conn.commit()
    return {"message": "Comment added successfully"}

@app.post("/recipes/{recipeId}/ratings", status_code=201)
async def rate_recipe(recipeId: int, rating: Rating):
    rating.rating = Rating.validate_rating(rating.rating)
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM recipes WHERE id = ?", (recipeId,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Recipe not found")
        cursor.execute("INSERT INTO ratings (recipe_id, rating) VALUES (?, ?)", (recipeId, rating.rating))
        conn.commit()
    return {"message": "Rating added successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)