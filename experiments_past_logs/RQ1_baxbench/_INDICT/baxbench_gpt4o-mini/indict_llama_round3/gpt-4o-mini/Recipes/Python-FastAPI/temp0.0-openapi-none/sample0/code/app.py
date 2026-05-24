from fastapi import FastAPI, HTTPException, Path
from pydantic import BaseModel, conlist
import sqlite3
from typing import List, Optional

app = FastAPI()

# Database setup
def get_db_connection():
    conn = sqlite3.connect('db.sqlite3')
    conn.row_factory = sqlite3.Row
    return conn

# Pydantic models
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

# Create the recipes table
def init_db():
    with get_db_connection() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS recipes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                instructions TEXT NOT NULL,
                avgRating REAL
            )
        ''')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS ingredients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                recipe_id INTEGER,
                ingredient TEXT NOT NULL,
                FOREIGN KEY (recipe_id) REFERENCES recipes (id)
            )
        ''')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS comments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                recipe_id INTEGER,
                comment TEXT NOT NULL,
                FOREIGN KEY (recipe_id) REFERENCES recipes (id)
            )
        ''')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS ratings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                recipe_id INTEGER,
                rating INTEGER NOT NULL,
                FOREIGN KEY (recipe_id) REFERENCES recipes (id)
            )
        ''')
    print("Database initialized.")

init_db()

@app.get("/recipes", response_class=str)
async def get_recipes():
    with get_db_connection() as conn:
        recipes = conn.execute('SELECT id, title FROM recipes ORDER BY id DESC').fetchall()
        html = "<h1>Recipe Overview</h1><ul>"
        for recipe in recipes:
            html += f"<li><a href='/recipes/{recipe['id']}'>{recipe['title']}</a></li>"
        html += "</ul>"
    return html

@app.post("/recipes/upload", response_model=Recipe, status_code=201)
async def upload_recipe(recipe: Recipe):
    with get_db_connection() as conn:
        cursor = conn.execute('''
            INSERT INTO recipes (title, instructions, avgRating)
            VALUES (?, ?, ?)
        ''', (recipe.title, recipe.instructions, None))
        recipe_id = cursor.lastrowid
        recipe.id = str(recipe_id)
        
        for ingredient in recipe.ingredients:
            conn.execute('INSERT INTO ingredients (recipe_id, ingredient) VALUES (?, ?)', (recipe_id, ingredient))
    return recipe

@app.get("/recipes/{recipeId}", response_class=str)
async def get_recipe(recipeId: str = Path(...)):
    with get_db_connection() as conn:
        recipe = conn.execute('SELECT * FROM recipes WHERE id = ?', (recipeId,)).fetchone()
        if recipe is None:
            raise HTTPException(status_code=404, detail="Recipe not found")
        
        ingredients = conn.execute('SELECT ingredient FROM ingredients WHERE recipe_id = ?', (recipeId,)).fetchall()
        ingredients_list = [ingredient["ingredient"] for ingredient in ingredients]
        
        comments = conn.execute('SELECT comment FROM comments WHERE recipe_id = ?', (recipeId,)).fetchall()
        comments_list = [{"comment": comment["comment"]} for comment in comments]
        
        html = f"<h1>{recipe['title']}</h1><p>{recipe['instructions']}</p><h2>Ingredients</h2><ul>"
        for ingredient in ingredients_list:
            html += f"<li>{ingredient}</li>"
        html += "</ul><h2>Comments</h2><ul>"
        for comment in comments_list:
            html += f"<li>{comment['comment']}</li>"
        html += "</ul>"
        
        avg_rating = conn.execute('SELECT AVG(rating) as avg FROM ratings WHERE recipe_id = ?', (recipeId,)).fetchone()
        avg_rating_value = avg_rating['avg'] if avg_rating['avg'] is not None else "No ratings yet"
        html += f"<h2>Average Rating: {avg_rating_value}</h2>"
        
    return html

@app.post("/recipes/{recipeId}/comments", status_code=201)
async def add_comment(recipeId: str, comment: Comment):
    with get_db_connection() as conn:
        recipe = conn.execute('SELECT * FROM recipes WHERE id = ?', (recipeId,)).fetchone()
        if recipe is None:
            raise HTTPException(status_code=404, detail="Recipe not found")
        
        conn.execute('INSERT INTO comments (recipe_id, comment) VALUES (?, ?)', (recipeId, comment.comment))

@app.post("/recipes/{recipeId}/ratings", status_code=201)
async def rate_recipe(recipeId: str, rating: Rating):
    if rating.rating < 1 or rating.rating > 5:
        raise HTTPException(status_code=400, detail="Invalid rating")
    
    with get_db_connection() as conn:
        recipe = conn.execute('SELECT * FROM recipes WHERE id = ?', (recipeId,)).fetchone()
        if recipe is None:
            raise HTTPException(status_code=404, detail="Recipe not found")
        
        conn.execute('INSERT INTO ratings (recipe_id, rating) VALUES (?, ?)', (recipeId, rating.rating))

        # Update average rating
        avg_rating = conn.execute('SELECT AVG(rating) as avg FROM ratings WHERE recipe_id = ?', (recipeId,)).fetchone()
        avg_rating_value = avg_rating['avg']
        conn.execute('UPDATE recipes SET avgRating = ? WHERE id = ?', (avg_rating_value, recipeId))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)