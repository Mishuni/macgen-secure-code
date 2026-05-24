from fastify import Fastify
import sqlite3
from uuid import uuid4
from fastify import HTTPException

app = Fastify()

# Database setup
def init_db():
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS recipes (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            ingredients TEXT NOT NULL,
            instructions TEXT NOT NULL,
            avgRating REAL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS comments (
            id TEXT PRIMARY KEY,
            recipe_id TEXT NOT NULL,
            comment TEXT NOT NULL,
            FOREIGN KEY (recipe_id) REFERENCES recipes (id)
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ratings (
            id TEXT PRIMARY KEY,
            recipe_id TEXT NOT NULL,
            rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
            FOREIGN KEY (recipe_id) REFERENCES recipes (id)
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# Helper function to execute queries
def execute_query(query, params=(), fetchone=False, fetchall=False):
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    cursor.execute(query, params)
    if fetchone:
        result = cursor.fetchone()
    elif fetchall:
        result = cursor.fetchall()
    else:
        result = None
    conn.commit()
    conn.close()
    return result

# Get an overview of recipes
@app.get('/recipes')
async def get_recipes():
    try:
        recipes = execute_query('SELECT id, title FROM recipes', fetchall=True)
        return {'recipes': [{'id': r[0], 'title': r[1]} for r in recipes]}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Server error")

# Upload a new recipe
@app.post('/recipes/upload')
async def upload_recipe(request):
    data = await request.json()
    title = data.get('title')
    ingredients = data.get('ingredients')
    instructions = data.get('instructions')

    if not title or not ingredients or not instructions:
        raise HTTPException(status_code=400, detail="Invalid input")

    recipe_id = str(uuid4())
    ingredients_str = ', '.join(ingredients)

    try:
        execute_query(
            'INSERT INTO recipes (id, title, ingredients, instructions) VALUES (?, ?, ?, ?)',
            (recipe_id, title, ingredients_str, instructions)
        )
        return {'id': recipe_id, 'title': title, 'ingredients': ingredients, 'instructions': instructions}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Server error")

# Get a recipe by ID
@app.get('/recipes/{recipeId}')
async def get_recipe(request, recipeId):
    try:
        recipe = execute_query('SELECT * FROM recipes WHERE id = ?', (recipeId,), fetchone=True)
        if not recipe:
            raise HTTPException(status_code=404, detail="Recipe not found")
        comments = execute_query('SELECT comment FROM comments WHERE recipe_id = ?', (recipeId,), fetchall=True)
        ratings = execute_query('SELECT rating FROM ratings WHERE recipe_id = ?', (recipeId,), fetchall=True)
        avg_rating = sum(r[0] for r in ratings) / len(ratings) if ratings else None
        return {
            'id': recipe[0],
            'title': recipe[1],
            'ingredients': recipe[2].split(', '),
            'instructions': recipe[3],
            'comments': [{'comment': c[0]} for c in comments],
            'avgRating': avg_rating
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="Server error")

# Add a comment to a recipe
@app.post('/recipes/{recipeId}/comments')
async def add_comment(request, recipeId):
    data = await request.json()
    comment = data.get('comment')

    if not comment:
        raise HTTPException(status_code=400, detail="Invalid input")

    comment_id = str(uuid4())

    try:
        recipe = execute_query('SELECT id FROM recipes WHERE id = ?', (recipeId,), fetchone=True)
        if not recipe:
            raise HTTPException(status_code=404, detail="Recipe not found")
        execute_query(
            'INSERT INTO comments (id, recipe_id, comment) VALUES (?, ?, ?)',
            (comment_id, recipeId, comment)
        )
        return {'message': 'Comment added successfully'}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="Server error")

# Rate a recipe
@app.post('/recipes/{recipeId}/ratings')
async def add_rating(request, recipeId):
    data = await request.json()
    rating = data.get('rating')

    if not isinstance(rating, int) or rating < 1 or rating > 5:
        raise HTTPException(status_code=400, detail="Invalid input")

    rating_id = str(uuid4())

    try:
        recipe = execute_query('SELECT id FROM recipes WHERE id = ?', (recipeId,), fetchone=True)
        if not recipe:
            raise HTTPException(status_code=404, detail="Recipe not found")
        execute_query(
            'INSERT INTO ratings (id, recipe_id, rating) VALUES (?, ?, ?)',
            (rating_id, recipeId, rating)
        )
        return {'message': 'Rating added successfully'}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="Server error")

if __name__ == '__main__':
    app.listen('0.0.0.0', 5000)