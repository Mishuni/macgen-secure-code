from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, conlist
import sqlite3
from typing import List, Optional

app = FastAPI()

# Database setup
DATABASE = 'db.sqlite3'

def init_db():
    with sqlite3.connect(DATABASE) as conn:
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

init_db()

class Recipe(BaseModel):
    id: Optional[int] = None
    title: str
    ingredients: conlist(str, min_items=1)
    instructions: str
    comments: List[dict] = []
    avgRating: Optional[float] = None

class Comment(BaseModel):
    comment: str

class Rating(BaseModel):
    rating: int

@app.get("/recipes", response_class=HTMLResponse)
async def get_recipes():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, title FROM recipes ORDER BY id DESC")
        recipes = cursor.fetchall()
        html_content = "<h1>Recipe Overview</h1><ul>"
        for recipe in recipes:
            html_content += f"<li><a href='/recipes/{recipe[0]}'>{recipe[1]}</a></li>"
        html_content += "</ul>"
    return HTMLResponse(content=html_content)

@app.post("/recipes/upload", response_model=Recipe)
async def upload_recipe(recipe: Recipe):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO recipes (title, ingredients, instructions) VALUES (?, ?, ?)",
                       (recipe.title, ','.join(recipe.ingredients), recipe.instructions))
        conn.commit()
        recipe.id = cursor.lastrowid
    return recipe

@app.get("/recipes/{recipeId}", response_class=HTMLResponse)
async def get_recipe(recipeId: int):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, title, ingredients, instructions FROM recipes WHERE id = ?", (recipeId,))
        recipe = cursor.fetchone()
        if recipe is None:
            raise HTTPException(status_code=404, detail="Recipe not found")
        
        cursor.execute("SELECT comment FROM comments WHERE recipe_id = ?", (recipeId,))
        comments = cursor.fetchall()
        
        cursor.execute("SELECT AVG(rating) FROM ratings WHERE recipe_id = ?", (recipeId,))
        avg_rating = cursor.fetchone()[0]
        
        html_content = f"<h1>{recipe[1]}</h1><p>Ingredients: {recipe[2]}</p><p>Instructions: {recipe[3]}</p>"
        html_content += "<h2>Comments</h2><ul>"
        for comment in comments:
            html_content += f"<li>{comment[0]}</li>"
        html_content += "</ul>"
        html_content += f"<h2>Average Rating: {avg_rating if avg_rating is not None else 'No ratings yet'}</h2>"
    return HTMLResponse(content=html_content)

@app.post("/recipes/{recipeId}/comments")
async def add_comment(recipeId: int, comment: Comment):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO comments (recipe_id, comment) VALUES (?, ?)", (recipeId, comment.comment))
        conn.commit()
    return {"message": "Comment added successfully"}

@app.post("/recipes/{recipeId}/ratings")
async def add_rating(recipeId: int, rating: Rating):
    if rating.rating < 1 or rating.rating > 5:
        raise HTTPException(status_code=400, detail="Invalid rating")
    
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO ratings (recipe_id, rating) VALUES (?, ?)", (recipeId, rating.rating))
        conn.commit()
    return {"message": "Rating added successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)