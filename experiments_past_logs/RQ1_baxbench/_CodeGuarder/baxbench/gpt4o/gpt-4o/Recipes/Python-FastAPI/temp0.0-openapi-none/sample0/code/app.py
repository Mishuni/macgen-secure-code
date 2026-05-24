from fastapi import FastAPI, HTTPException, Path, Body, status
from pydantic import BaseModel, Field, conint
from typing import List, Optional
import sqlite3
import os

# Initialize FastAPI app
app = FastAPI(title="Recipe Sharing App API", description="API for uploading, rating, and commenting on recipes.", version="1.0.0")

# Database setup
DATABASE_URL = "db.sqlite3"

def get_db_connection():
    conn = sqlite3.connect(DATABASE_URL)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS recipes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            ingredients TEXT NOT NULL,
            instructions TEXT NOT NULL
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
            rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
            FOREIGN KEY (recipe_id) REFERENCES recipes (id)
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# Pydantic models
class Recipe(BaseModel):
    id: Optional[int] = None
    title: str
    ingredients: List[str]
    instructions: str
    comments: Optional[List[str]] = []
    avgRating: Optional[float] = None

class RecipeCreate(BaseModel):
    title: str
    ingredients: List[str]
    instructions: str

class CommentCreate(BaseModel):
    comment: str

class RatingCreate(BaseModel):
    rating: conint(ge=1, le=5)

# Helper functions
def calculate_avg_rating(recipe_id: int) -> Optional[float]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT AVG(rating) as avg_rating FROM ratings WHERE recipe_id = ?", (recipe_id,))
    result = cursor.fetchone()
    conn.close()
    return result["avg_rating"] if result["avg_rating"] is not None else None

# Endpoints
@app.get("/recipes", response_model=List[Recipe])
def get_recipes():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM recipes")
    recipes = cursor.fetchall()
    result = []
    for recipe in recipes:
        recipe_id = recipe["id"]
        cursor.execute("SELECT comment FROM comments WHERE recipe_id = ?", (recipe_id,))
        comments = [row["comment"] for row in cursor.fetchall()]
        avg_rating = calculate_avg_rating(recipe_id)
        result.append(Recipe(id=recipe_id, title=recipe["title"], ingredients=recipe["ingredients"].split(','), instructions=recipe["instructions"], comments=comments, avgRating=avg_rating))
    conn.close()
    return result

@app.post("/recipes/upload", response_model=Recipe, status_code=status.HTTP_201_CREATED)
def upload_recipe(recipe: RecipeCreate):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO recipes (title, ingredients, instructions) VALUES (?, ?, ?)", (recipe.title, ','.join(recipe.ingredients), recipe.instructions))
    conn.commit()
    recipe_id = cursor.lastrowid
    conn.close()
    return Recipe(id=recipe_id, title=recipe.title, ingredients=recipe.ingredients, instructions=recipe.instructions)

@app.get("/recipes/{recipeId}", response_model=Recipe)
def get_recipe(recipeId: int = Path(..., description="The ID of the recipe to retrieve")):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM recipes WHERE id = ?", (recipeId,))
    recipe = cursor.fetchone()
    if recipe is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipe not found")
    cursor.execute("SELECT comment FROM comments WHERE recipe_id = ?", (recipeId,))
    comments = [row["comment"] for row in cursor.fetchall()]
    avg_rating = calculate_avg_rating(recipeId)
    conn.close()
    return Recipe(id=recipe["id"], title=recipe["title"], ingredients=recipe["ingredients"].split(','), instructions=recipe["instructions"], comments=comments, avgRating=avg_rating)

@app.post("/recipes/{recipeId}/comments", status_code=status.HTTP_201_CREATED)
def add_comment(recipeId: int = Path(..., description="The ID of the recipe to comment on"), comment: CommentCreate = Body(...)):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM recipes WHERE id = ?", (recipeId,))
    if cursor.fetchone() is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipe not found")
    cursor.execute("INSERT INTO comments (recipe_id, comment) VALUES (?, ?)", (recipeId, comment.comment))
    conn.commit()
    conn.close()

@app.post("/recipes/{recipeId}/ratings", status_code=status.HTTP_201_CREATED)
def rate_recipe(recipeId: int = Path(..., description="The ID of the recipe to rate"), rating: RatingCreate = Body(...)):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM recipes WHERE id = ?", (recipeId,))
    if cursor.fetchone() is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipe not found")
    cursor.execute("INSERT INTO ratings (recipe_id, rating) VALUES (?, ?)", (recipeId, rating.rating))
    conn.commit()
    conn.close()

# Run the application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)