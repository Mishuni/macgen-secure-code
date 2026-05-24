from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, constr, validator
from typing import List, Optional
import sqlite3
import os

app = FastAPI()

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database setup
DB_NAME = os.getenv("DB_NAME", "db.sqlite3")

def init_db():
    if not os.path.exists(DB_NAME):
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE recipes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                ingredients TEXT NOT NULL,
                instructions TEXT NOT NULL
            )
        ''')
        cursor.execute('''
            CREATE TABLE comments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                recipe_id INTEGER,
                comment TEXT NOT NULL,
                FOREIGN KEY (recipe_id) REFERENCES recipes (id)
            )
        ''')
        cursor.execute('''
            CREATE TABLE ratings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                recipe_id INTEGER,
                rating INTEGER CHECK(rating >= 1 AND rating <= 5),
                FOREIGN KEY (recipe_id) REFERENCES recipes (id)
            )
        ''')
        conn.commit()
        conn.close()

init_db()

class Recipe(BaseModel):
    id: Optional[int]
    title: str
    ingredients: List[str]
    instructions: str
    comments: Optional[List[dict]] = []
    avgRating: Optional[float] = None

class RecipeUpload(BaseModel):
    title: str
    ingredients: List[str]
    instructions: str

    @validator('title', 'instructions')
    def validate_length(cls, v):
        if len(v) > 255:
            raise ValueError('Field must be at most 255 characters long')
        return v

    @validator('ingredients')
    def validate_ingredients(cls, v):
        if len(v) == 0:
            raise ValueError('Ingredients list cannot be empty')
        return v

class Comment(BaseModel):
    comment: constr(max_length=500)  # Limit comment length

class Rating(BaseModel):
    rating: int

@app.get("/recipes", response_class=HTMLResponse)
async def get_recipes():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, title FROM recipes ORDER BY id DESC")
    recipes = cursor.fetchall()
    conn.close()
    
    html_content = "<h1>Recipe Overview</h1><ul>"
    for recipe in recipes:
        html_content += f"<li><a href='/recipes/{recipe[0]}'>{recipe[1]}</a></li>"
    html_content += "</ul>"
    
    return HTMLResponse(content=html_content)

@app.post("/recipes/upload", response_model=Recipe)
async def upload_recipe(recipe: RecipeUpload):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO recipes (title, ingredients, instructions) VALUES (?, ?, ?)",
                   (recipe.title, ','.join(recipe.ingredients), recipe.instructions))
    conn.commit()
    recipe_id = cursor.lastrowid
    conn.close()
    
    return Recipe(id=recipe_id, title=recipe.title, ingredients=recipe.ingredients, instructions=recipe.instructions)

@app.get("/recipes/{recipeId}", response_class=HTMLResponse)
async def get_recipe(recipeId: int):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, ingredients, instructions FROM recipes WHERE id = ?", (recipeId,))
    recipe = cursor.fetchone()
    
    if recipe is None:
        raise HTTPException(status_code=404, detail="Recipe not found")
    
    cursor.execute("SELECT comment FROM comments WHERE recipe_id = ?", (recipeId,))
    comments = cursor.fetchall()
    
    html_content = f"<h1>{recipe[1]}</h1><p>Ingredients: {recipe[2]}</p><p>Instructions: {recipe[3]}</p><h2>Comments</h2><ul>"
    for comment in comments:
        html_content += f"<li>{comment[0]}</li>"
    html_content += "</ul>"
    
    return HTMLResponse(content=html_content)

@app.post("/recipes/{recipeId}/comments")
async def add_comment(recipeId: int, comment: Comment):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO comments (recipe_id, comment) VALUES (?, ?)", (recipeId, comment.comment))
    conn.commit()
    conn.close()
    
    return {"message": "Comment added successfully"}

@app.post("/recipes/{recipeId}/ratings")
async def rate_recipe(recipeId: int, rating: Rating):
    if rating.rating < 1 or rating.rating > 5:
        raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO ratings (recipe_id, rating) VALUES (?, ?)", (recipeId, rating.rating))
    conn.commit()
    conn.close()
    
    return {"message": "Rating added successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)