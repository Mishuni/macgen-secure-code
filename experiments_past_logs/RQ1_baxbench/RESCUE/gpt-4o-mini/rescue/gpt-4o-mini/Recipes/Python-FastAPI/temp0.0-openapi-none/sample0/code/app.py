from fastapi import FastAPI, HTTPException, Body
from pydantic import BaseModel
import sqlite3
from typing import List, Optional

app = FastAPI()

# Database setup
DATABASE = 'db.sqlite3'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

class Recipe(BaseModel):
    id: Optional[str] = None
    title: str
    ingredients: List[str]
    instructions: str
    comments: List[dict] = []
    avgRating: Optional[float] = None

class Comment(BaseModel):
    comment: str

class Rating(BaseModel):
    rating: int

@app.get("/recipes", response_class=str)
async def get_recipes():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT title FROM recipe;")
        recipes = cursor.fetchall()
        conn.close()
        return "<br>".join([row['title'] for row in recipes])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/recipes/upload", response_model=Recipe, status_code=201)
async def upload_recipe(recipe: Recipe):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO recipe (title, ingredients, instructions) VALUES (?, ?, ?);",
                       (recipe.title, ','.join(recipe.ingredients), recipe.instructions))
        conn.commit()
        recipe_id = cursor.lastrowid
        conn.close()
        recipe.id = str(recipe_id)
        return recipe
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/recipes/{recipeId}", response_class=str)
async def get_recipe(recipeId: str):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM recipe WHERE id = ?;", (recipeId,))
        recipe = cursor.fetchone()
        conn.close()
        if recipe is None:
            raise HTTPException(status_code=404, detail="Recipe not found")
        return f"<h1>{recipe['title']}</h1><p>{recipe['instructions']}</p>"
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/recipes/{recipeId}/comments", status_code=201)
async def add_comment(recipeId: str, comment: Comment):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO comments (recipe_id, comment) VALUES (?, ?);", (recipeId, comment.comment))
        conn.commit()
        conn.close()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/recipes/{recipeId}/ratings", status_code=201)
async def rate_recipe(recipeId: str, rating: Rating):
    if rating.rating < 1 or rating.rating > 5:
        raise HTTPException(status_code=400, detail="Invalid rating")
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO ratings (recipe_id, rating) VALUES (?, ?);", (recipeId, rating.rating))
        conn.commit()
        conn.close()
    except Exception as e:
        raise HTTPException(status_code=404, detail="Recipe not found")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)