
from fastapi import FastAPI, HTTPException, Path
from pydantic import BaseModel, Field
from typing import List, Optional
import sqlite3
from fastapi.responses import HTMLResponse, JSONResponse

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

class RecipeUpload(BaseModel):
    title: str
    ingredients: List[str]
    instructions: str

class Comment(BaseModel):
    comment: str

class Rating(BaseModel):
    rating: int = Field(..., ge=1, le=5)

# Helper functions
def get_db_connection():
    conn = sqlite3.connect('db.sqlite3')
    conn.row_factory = sqlite3.Row
    return conn

def calculate_avg_rating(recipe_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT AVG(rating) as avg_rating FROM ratings WHERE recipe_id = ?', (recipe_id,))
    avg_rating = cursor.fetchone()['avg_rating']
    conn.close()
    return avg_rating

# Endpoints
@app.get("/recipes", response_class=HTMLResponse)
async def get_recipes():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id, title FROM recipes')
    recipes = cursor.fetchall()
    conn.close()
    html_content = "<h1>Recipes</h1><ul>"
    for recipe in recipes:
        html_content += f'<li><a href="/recipes/{recipe["id"]}">{recipe["title"]}</a></li>'
    html_content += "</ul>"
    return html_content

@app.post("/recipes/upload", response_model=Recipe, status_code=201)
async def upload_recipe(recipe: RecipeUpload):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO recipes (title, ingredients, instructions) VALUES (?, ?, ?)',
                   (recipe.title, ','.join(recipe.ingredients), recipe.instructions))
    conn.commit()
    recipe_id = cursor.lastrowid
    conn.close()
    return {**recipe.dict(), "id": recipe_id, "comments": [], "avgRating": None}

@app.get("/recipes/{recipeId}", response_class=HTMLResponse)
async def get_recipe(recipeId: int = Path(..., description="The ID of the recipe to retrieve")):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM recipes WHERE id = ?', (recipeId,))
    recipe = cursor.fetchone()
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    
    cursor.execute('SELECT comment FROM comments WHERE recipe_id = ?', (recipeId,))
    comments = [row['comment'] for row in cursor.fetchall()]
    
    avg_rating = calculate_avg_rating(recipeId)
    
    conn.close()
    
    html_content = f"<h1>{recipe['title']}</h1>"
    html_content += f"<p>Ingredients: {recipe['ingredients']}</p>"
    html_content += f"<p>Instructions: {recipe['instructions']}</p>"
    html_content += f"<p>Average Rating: {avg_rating if avg_rating else 'No ratings yet'}</p>"
    html_content += "<h2>Comments</h2><ul>"
    for comment in comments:
        html_content += f"<li>{comment}</li>"
    html_content += "</ul>"
    return html_content

@app.post("/recipes/{recipeId}/comments", status_code=201)
async def add_comment(recipeId: int, comment: Comment):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM recipes WHERE id = ?', (recipeId,))
    if not cursor.fetchone():
        raise HTTPException(status_code=404, detail="Recipe not found")
    
    cursor.execute('INSERT INTO comments (recipe_id, comment) VALUES (?, ?)', (recipeId, comment.comment))
    conn.commit()
    conn.close()
    return JSONResponse(status_code=201, content={"message": "Comment added successfully"})

@app.post("/recipes/{recipeId}/ratings", status_code=201)
async def rate_recipe(recipeId: int, rating: Rating):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM recipes WHERE id = ?', (recipeId,))
    if not cursor.fetchone():
        raise HTTPException(status_code=404, detail="Recipe not found")
    
    cursor.execute('INSERT INTO ratings (recipe_id, rating) VALUES (?, ?)', (recipeId, rating.rating))
    conn.commit()
    conn.close()
    return JSONResponse(status_code=201, content={"message": "Rating added successfully"})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)