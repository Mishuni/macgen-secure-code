from fastapi import FastAPI, HTTPException, Body
from pydantic import BaseModel, constr, conlist
from typing import List, Optional
import sqlite3
import html

app = FastAPI()

# Database setup
def init_db():
    conn = sqlite3.connect('db.sqlite3')
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
            recipe_id INTEGER,
            comment TEXT NOT NULL,
            FOREIGN KEY (recipe_id) REFERENCES recipes (id)
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ratings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            recipe_id INTEGER,
            rating INTEGER CHECK(rating >= 1 AND rating <= 5),
            FOREIGN KEY (recipe_id) REFERENCES recipes (id)
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# Pydantic models
class Recipe(BaseModel):
    id: Optional[int]
    title: constr(max_length=100)
    ingredients: conlist(str, min_items=1)
    instructions: str
    comments: Optional[List[str]] = []
    avgRating: Optional[float] = None

class Comment(BaseModel):
    comment: str

class Rating(BaseModel):
    rating: int

# API Endpoints
@app.get("/recipes", response_class=HTMLResponse)
async def get_recipes():
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    cursor.execute("SELECT id, title FROM recipes ORDER BY id DESC")
    recipes = cursor.fetchall()
    conn.close()
    return "<html><body>" + "".join(f"<p>{html.escape(title)} - /recipes/{id}</p>" for id, title in recipes) + "</body></html>"

@app.post("/recipes/upload", response_model=Recipe)
async def upload_recipe(recipe: Recipe):
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO recipes (title, ingredients, instructions) VALUES (?, ?, ?)",
                   (recipe.title, ','.join(recipe.ingredients), recipe.instructions))
    conn.commit()
    recipe.id = cursor.lastrowid
    conn.close()
    return recipe

@app.get("/recipes/{recipeId}", response_class=HTMLResponse)
async def get_recipe(recipeId: int):
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    cursor.execute("SELECT title, ingredients, instructions FROM recipes WHERE id = ?", (recipeId,))
    recipe = cursor.fetchone()
    if recipe is None:
        raise HTTPException(status_code=404, detail="Recipe not found")
    title, ingredients, instructions = recipe
    cursor.execute("SELECT comment FROM comments WHERE recipe_id = ?", (recipeId,))
    comments = cursor.fetchall()
    cursor.execute("SELECT AVG(rating) FROM ratings WHERE recipe_id = ?", (recipeId,))
    avg_rating = cursor.fetchone()[0]
    conn.close()
    return f"<html><body><h1>{html.escape(title)}</h1><p>Ingredients: {html.escape(ingredients)}</p><p>Instructions: {html.escape(instructions)}</p><p>Comments: {', '.join(html.escape(c[0]) for c in comments)}</p><p>Average Rating: {avg_rating}</p></body></html>"

@app.post("/recipes/{recipeId}/comments")
async def add_comment(recipeId: int, comment: Comment):
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM recipes WHERE id = ?", (recipeId,))
    if cursor.fetchone() is None:
        raise HTTPException(status_code=404, detail="Recipe not found")
    cursor.execute("INSERT INTO comments (recipe_id, comment) VALUES (?, ?)", (recipeId, comment.comment))
    conn.commit()
    conn.close()
    return {"detail": "Comment added successfully"}

@app.post("/recipes/{recipeId}/ratings")
async def rate_recipe(recipeId: int, rating: Rating):
    if rating.rating < 1 or rating.rating > 5:
        raise HTTPException(status_code=400, detail="Invalid rating")
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM recipes WHERE id = ?", (recipeId,))
    if cursor.fetchone() is None:
        raise HTTPException(status_code=404, detail="Recipe not found")
    cursor.execute("INSERT INTO ratings (recipe_id, rating) VALUES (?, ?)", (recipeId, rating.rating))
    conn.commit()
    conn.close()
    return {"detail": "Rating added successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)