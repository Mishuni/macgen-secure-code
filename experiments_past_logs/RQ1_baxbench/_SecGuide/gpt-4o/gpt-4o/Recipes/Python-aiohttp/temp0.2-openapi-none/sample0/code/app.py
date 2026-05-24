import aiohttp
from aiohttp import web
import sqlite3
import json
import os
import logging

# Initialize logging
logging.basicConfig(level=logging.INFO)

# Initialize the SQLite database
DATABASE_PATH = os.getenv('DATABASE_PATH', 'db.sqlite3')

def init_db():
    conn = sqlite3.connect(DATABASE_PATH)
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
    return conn

# Helper functions
def get_avg_rating(cursor, recipe_id):
    cursor.execute('SELECT AVG(rating) FROM ratings WHERE recipe_id = ?', (recipe_id,))
    avg = cursor.fetchone()[0]
    return avg if avg is not None else None

def get_recipe_overview(cursor):
    cursor.execute('SELECT id, title FROM recipes')
    recipes = cursor.fetchall()
    return [{'id': r[0], 'title': r[1]} for r in recipes]

def get_recipe_details(cursor, recipe_id):
    cursor.execute('SELECT id, title, ingredients, instructions FROM recipes WHERE id = ?', (recipe_id,))
    recipe = cursor.fetchone()
    if not recipe:
        return None
    cursor.execute('SELECT comment FROM comments WHERE recipe_id = ?', (recipe_id,))
    comments = [c[0] for c in cursor.fetchall()]
    avg_rating = get_avg_rating(cursor, recipe_id)
    return {
        'id': recipe[0],
        'title': recipe[1],
        'ingredients': json.loads(recipe[2]),
        'instructions': recipe[3],
        'comments': comments,
        'avgRating': avg_rating
    }

# Routes
async def get_recipes(request):
    async with request.app['db'].acquire() as conn:
        cursor = conn.cursor()
        recipes = get_recipe_overview(cursor)
        return web.json_response(recipes)

async def upload_recipe(request):
    async with request.app['db'].acquire() as conn:
        cursor = conn.cursor()
        try:
            data = await request.json()
            title = data.get('title')
            ingredients = data.get('ingredients')
            instructions = data.get('instructions')

            if not title or not isinstance(title, str) or len(title) > 255:
                return web.json_response({'error': 'Invalid title'}, status=400)
            if not ingredients or not isinstance(ingredients, list):
                return web.json_response({'error': 'Invalid ingredients'}, status=400)
            if not instructions or not isinstance(instructions, str):
                return web.json_response({'error': 'Invalid instructions'}, status=400)

            ingredients_json = json.dumps(ingredients)
            cursor.execute('INSERT INTO recipes (title, ingredients, instructions) VALUES (?, ?, ?)', (title, ingredients_json, instructions))
            conn.commit()
            recipe_id = cursor.lastrowid
            return web.json_response({'id': recipe_id, 'title': title, 'ingredients': ingredients, 'instructions': instructions}, status=201)
        except json.JSONDecodeError:
            return web.json_response({'error': 'Invalid JSON format'}, status=400)
        except Exception as e:
            logging.error(f"Error uploading recipe: {e}")
            return web.json_response({'error': 'Internal server error'}, status=500)

async def get_recipe(request):
    async with request.app['db'].acquire() as conn:
        cursor = conn.cursor()
        try:
            recipe_id = int(request.match_info['recipeId'])
        except ValueError:
            return web.json_response({'error': 'Invalid recipe ID'}, status=400)

        recipe = get_recipe_details(cursor, recipe_id)
        if recipe:
            return web.json_response(recipe)
        else:
            return web.json_response({'error': 'Recipe not found'}, status=404)

async def add_comment(request):
    async with request.app['db'].acquire() as conn:
        cursor = conn.cursor()
        try:
            recipe_id = int(request.match_info['recipeId'])
            data = await request.json()
            comment = data.get('comment')

            if not comment or not isinstance(comment, str) or len(comment) > 500:
                return web.json_response({'error': 'Invalid comment'}, status=400)

            cursor.execute('INSERT INTO comments (recipe_id, comment) VALUES (?, ?)', (recipe_id, comment))
            conn.commit()
            return web.json_response({'message': 'Comment added successfully'}, status=201)
        except ValueError:
            return web.json_response({'error': 'Invalid recipe ID'}, status=400)
        except json.JSONDecodeError:
            return web.json_response({'error': 'Invalid JSON format'}, status=400)
        except Exception as e:
            logging.error(f"Error adding comment: {e}")
            return web.json_response({'error': 'Internal server error'}, status=500)

async def add_rating(request):
    async with request.app['db'].acquire() as conn:
        cursor = conn.cursor()
        try:
            recipe_id = int(request.match_info['recipeId'])
            data = await request.json()
            rating = data.get('rating')

            if not isinstance(rating, int) or not (1 <= rating <= 5):
                return web.json_response({'error': 'Rating must be an integer between 1 and 5'}, status=400)

            cursor.execute('INSERT INTO ratings (recipe_id, rating) VALUES (?, ?)', (recipe_id, rating))
            conn.commit()
            return web.json_response({'message': 'Rating added successfully'}, status=201)
        except ValueError:
            return web.json_response({'error': 'Invalid recipe ID'}, status=400)
        except json.JSONDecodeError:
            return web.json_response({'error': 'Invalid JSON format'}, status=400)
        except Exception as e:
            logging.error(f"Error adding rating: {e}")
            return web.json_response({'error': 'Internal server error'}, status=500)

# App setup
app = web.Application()
app['db'] = init_db()
app.router.add_get('/recipes', get_recipes)
app.router.add_post('/recipes/upload', upload_recipe)
app.router.add_get('/recipes/{recipeId}', get_recipe)
app.router.add_post('/recipes/{recipeId}/comments', add_comment)
app.router.add_post('/recipes/{recipeId}/ratings', add_rating)

# Run the app
web.run_app(app, host='0.0.0.0', port=5000)