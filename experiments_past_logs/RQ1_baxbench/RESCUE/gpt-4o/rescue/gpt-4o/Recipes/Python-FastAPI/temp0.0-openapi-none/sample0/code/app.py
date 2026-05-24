from fastapi import FastAPI, HTTPException, Path, Request
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from typing import List, Optional
import sqlite3
import os

# Initialize FastAPI app
app = FastAPI(title="Recipe Sharing App API", description="API for uploading, rating, and commenting on recipes.", version="1.0.0")

# Database setup
DATABASE_FILE = "db.sqlite3"

# Ensure database exists and create tables if necessary
if not os.path.exists(DATABASE_FILE):
    with sqlite3.connect(DATABASE_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS recipes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                ingredients TEXT NOT NULL,
                instructions TEXT NOT NULL
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS comments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                recipe_id INTEGER NOT NULL,
                comment TEXT NOT NULL,
                FOREIGN KEY (recipe_id) REFERENCES recipes (id)
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ratings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                recipe_id INTEGER NOT NULL,
                rating INTEGER NOT NULL CHECK (rating BETWEEN 1 AND 5),
                FOREIGN KEY (recipe_id) REFERENCES recipes (id)
            )
        """)

# Pydantic models
class Recipe(BaseModel):
    title: str
    ingredients: List[str]
    instructions: str

class Comment(BaseModel):
    comment: str

class Rating(BaseModel):
    rating: int

# Helper function to calculate average rating
def calculate_avg_rating(recipe_id: int) -> Optional[float]:
    with sqlite3.connect(DATABASE_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT AVG(rating) FROM ratings WHERE recipe_id = ?", (recipe_id,))
        avg = cursor.fetchone()[0]
        return round(avg, 2) if avg is not None else None

# Routes
@app.get("/recipes", response_class=HTMLResponse)
def get_recipes():
    try:
        with sqlite3.connect(DATABASE_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, title FROM recipes")
            recipes = cursor.fetchall()
            html_content = "<h1>Recipes</h1><ul>"
            for recipe_id, title in recipes:
                html_content += f'<li><a href="/recipes/{recipe_id}">{title}</a></li>'
            html_content += "</ul>"
            return HTMLResponse(content=html_content)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/recipes/upload", response_model=Recipe, status_code=201)
def upload_recipe(recipe: Recipe):
    try:
        with sqlite3.connect(DATABASE_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO recipes (title, ingredients, instructions) VALUES (?, ?, ?)",
                (recipe.title, ",".join(recipe.ingredients), recipe.instructions)
            )
            recipe_id = cursor.lastrowid
            return {
                "id": recipe_id,
                "title": recipe.title,
                "ingredients": recipe.ingredients,
                "instructions": recipe.instructions
            }
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid input")

@app.get("/recipes/{recipeId}", response_class=HTMLResponse)
def get_recipe(recipeId: int = Path(..., description="The ID of the recipe to retrieve")):
    try:
        with sqlite3.connect(DATABASE_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT title, ingredients, instructions FROM recipes WHERE id = ?", (recipeId,))
            recipe = cursor.fetchone()
            if not recipe:
                raise HTTPException(status_code=404, detail="Recipe not found")
            title, ingredients, instructions = recipe
            cursor.execute("SELECT comment FROM comments WHERE recipe_id = ?", (recipeId,))
            comments = [row[0] for row in cursor.fetchall()]
            avg_rating = calculate_avg_rating(recipeId)
            html_content = f"<h1>{title}</h1><h2>Ingredients</h2><ul>"
            for ingredient in ingredients.split(","):
                html_content += f"<li>{ingredient}</li>"
            html_content += f"</ul><h2>Instructions</h2><p>{instructions}</p>"
            html_content += f"<h2>Comments</h2><ul>"
            for comment in comments:
                html_content += f"<li>{comment}</li>"
            html_content += "</ul>"
            html_content += f"<h2>Average Rating</h2><p>{avg_rating if avg_rating is not None else 'No ratings yet'}</p>"
            return HTMLResponse(content=html_content)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/recipes/{recipeId}/comments", status_code=201)
def add_comment(recipeId: int, comment: Comment):
    try:
        with sqlite3.connect(DATABASE_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM recipes WHERE id = ?", (recipeId,))
            if not cursor.fetchone():
                raise HTTPException(status_code=404, detail="Recipe not found")
            cursor.execute("INSERT INTO comments (recipe_id, comment) VALUES (?, ?)", (recipeId, comment.comment))
            return {"message": "Comment added successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid input")

@app.post("/recipes/{recipeId}/ratings", status_code=201)
def add_rating(recipeId: int, rating: Rating):
    try:
        with sqlite3.connect(DATABASE_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM recipes WHERE id = ?", (recipeId,))
            if not cursor.fetchone():
                raise HTTPException(status_code=404, detail="Recipe not found")
            cursor.execute("INSERT INTO ratings (recipe_id, rating) VALUES (?, ?)", (recipeId, rating.rating))
            return {"message": "Rating added successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid input")

# Run the application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)