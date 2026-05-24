from fastapi import FastAPI, HTTPException, Path
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel, constr, conlist
import sqlite3
from typing import List, Optional

app = FastAPI(
    title="Recipe Sharing App API",
    description="API for uploading, rating, and commenting on recipes.",
    version="1.0.0"
)

DATABASE = "db.sqlite3"

# Database setup
def init_db():
    conn = sqlite3.connect(DATABASE)
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
            rating INTEGER NOT NULL,
            FOREIGN KEY (recipe_id) REFERENCES recipes (id)
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# Pydantic models
class Recipe(BaseModel):
    id: Optional[int]
    title: str
    ingredients: List[str]
    instructions: str
    comments: Optional[List[str]] = []
    avgRating: Optional[float] = None

class RecipeCreate(BaseModel):
    title: constr(min_length=1, max_length=100)
    ingredients: conlist(constr(min_length=1, max_length=100), min_items=1)
    instructions: constr(min_length=1)

class CommentCreate(BaseModel):
    comment: constr(min_length=1, max_length=500)

class RatingCreate(BaseModel):
    rating: int

# Helper functions
def calculate_avg_rating(recipe_id: int) -> Optional[float]:
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('SELECT AVG(rating) FROM ratings WHERE recipe_id = ?', (recipe_id,))
    avg_rating = cursor.fetchone()[0]
    conn.close()
    return avg_rating

# Routes
@app.get("/recipes", response_class=HTMLResponse)
async def get_recipes():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('SELECT id, title FROM recipes')
    recipes = cursor.fetchall()
    conn.close()
    html_content = "<h1>Recipes</h1><ul>"
    for recipe in recipes:
        html_content += f'<li><a href="/recipes/{recipe[0]}">{recipe[1]}</a></li>'
    html_content += "</ul>"
    return html_content

@app.post("/recipes/upload", response_model=Recipe, status_code=201)
async def upload_recipe(recipe: RecipeCreate):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO recipes (title, ingredients, instructions) VALUES (?, ?, ?)',
                   (recipe.title, ','.join(recipe.ingredients), recipe.instructions))
    recipe_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return Recipe(id=recipe_id, title=recipe.title, ingredients=recipe.ingredients, instructions=recipe.instructions)

@app.get("/recipes/{recipeId}", response_class=HTMLResponse)
async def get_recipe(recipeId: int = Path(..., description="The ID of the recipe to retrieve")):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('SELECT title, ingredients, instructions FROM recipes WHERE id = ?', (recipeId,))
    recipe = cursor.fetchone()
    if not recipe:
        conn.close()
        raise HTTPException(status_code=404, detail="Recipe not found")
    
    cursor.execute('SELECT comment FROM comments WHERE recipe_id = ?', (recipeId,))
    comments = [row[0] for row in cursor.fetchall()]
    
    avg_rating = calculate_avg_rating(recipeId)
    
    conn.close()
    
    html_content = f"<h1>{recipe[0]}</h1><p>Ingredients: {recipe[1]}</p><p>Instructions: {recipe[2]}</p>"
    html_content += "<h2>Comments</h2><ul>"
    for comment in comments:
        html_content += f"<li>{comment}</li>"
    html_content += "</ul>"
    html_content += f"<p>Average Rating: {avg_rating if avg_rating is not None else 'No ratings yet'}</p>"
    return html_content

@app.post("/recipes/{recipeId}/comments", status_code=201)
async def add_comment(recipeId: int, comment: CommentCreate):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM recipes WHERE id = ?', (recipeId,))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail="Recipe not found")
    
    cursor.execute('INSERT INTO comments (recipe_id, comment) VALUES (?, ?)', (recipeId, comment.comment))
    conn.commit()
    conn.close()
    return {"message": "Comment added successfully"}

@app.post("/recipes/{recipeId}/ratings", status_code=201)
async def rate_recipe(recipeId: int, rating: RatingCreate):
    if rating.rating < 1 or rating.rating > 5:
        raise HTTPException(status_code=400, detail="Invalid rating value")
    
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM recipes WHERE id = ?', (recipeId,))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail="Recipe not found")
    
    cursor.execute('INSERT INTO ratings (recipe_id, rating) VALUES (?, ?)', (recipeId, rating.rating))
    conn.commit()
    conn.close()
    return {"message": "Rating added successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)