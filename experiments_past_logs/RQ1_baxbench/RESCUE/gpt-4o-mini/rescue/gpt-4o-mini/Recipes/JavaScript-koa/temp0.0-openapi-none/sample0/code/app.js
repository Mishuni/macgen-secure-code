const Koa = require('koa');
const Router = require('koa-router');
const bodyParser = require('koa-bodyparser');
const sqlite3 = require('sqlite3').verbose();
const { open } = require('sqlite');

const app = new Koa();
const router = new Router();

// Open SQLite database
const dbPromise = open({
    filename: 'db.sqlite3',
    driver: sqlite3.Database
});

// Middleware to handle errors
app.use(async (ctx, next) => {
    try {
        await next();
    } catch (err) {
        ctx.status = err.status || 500;
        ctx.body = { error: err.message };
    }
});

// Middleware to parse JSON bodies
app.use(bodyParser());

// Initialize database and create tables if they don't exist
const initDb = async () => {
    const db = await dbPromise;
    await db.exec(`
        CREATE TABLE IF NOT EXISTS recipes (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            ingredients TEXT NOT NULL,
            instructions TEXT NOT NULL
        );
    `);
    await db.exec(`
        CREATE TABLE IF NOT EXISTS comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            recipeId TEXT NOT NULL,
            comment TEXT NOT NULL,
            FOREIGN KEY (recipeId) REFERENCES recipes (id)
        );
    `);
    await db.exec(`
        CREATE TABLE IF NOT EXISTS ratings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            recipeId TEXT NOT NULL,
            rating INTEGER NOT NULL CHECK(rating >= 1 AND rating <= 5),
            FOREIGN KEY (recipeId) REFERENCES recipes (id)
        );
    `);
};

// Get overview of recipes
router.get('/recipes', async (ctx) => {
    const db = await dbPromise;
    const recipes = await db.all('SELECT id, title FROM recipes');
    ctx.body = recipes;
});

// Upload a new recipe
router.post('/recipes/upload', async (ctx) => {
    const { title, ingredients, instructions } = ctx.request.body;
    if (!title || !ingredients || !instructions) {
        ctx.throw(400, 'Invalid input');
    }
    const db = await dbPromise;
    const id = require('uuid').v4();
    await db.run('INSERT INTO recipes (id, title, ingredients, instructions) VALUES (?, ?, ?, ?)', [id, title, JSON.stringify(ingredients), instructions]);
    ctx.status = 201;
    ctx.body = { id, title, ingredients, instructions };
});

// Get a recipe by its ID
router.get('/recipes/:recipeId', async (ctx) => {
    const { recipeId } = ctx.params;
    const db = await dbPromise;
    const recipe = await db.get('SELECT * FROM recipes WHERE id = ?', [recipeId]);
    if (!recipe) {
        ctx.throw(404, 'Recipe not found');
    }
    const comments = await db.all('SELECT comment FROM comments WHERE recipeId = ?', [recipeId]);
    const ratings = await db.all('SELECT rating FROM ratings WHERE recipeId = ?', [recipeId]);
    const avgRating = ratings.length > 0 ? ratings.reduce((sum, r) => sum + r.rating, 0) / ratings.length : null;
    ctx.body = { ...recipe, comments, avgRating };
});

// Add a comment to a recipe
router.post('/recipes/:recipeId/comments', async (ctx) => {
    const { recipeId } = ctx.params;
    const { comment } = ctx.request.body;
    if (!comment) {
        ctx.throw(400, 'Invalid input');
    }
    const db = await dbPromise;
    const recipe = await db.get('SELECT * FROM recipes WHERE id = ?', [recipeId]);
    if (!recipe) {
        ctx.throw(404, 'Recipe not found');
    }
    await db.run('INSERT INTO comments (recipeId, comment) VALUES (?, ?)', [recipeId, comment]);
    ctx.status = 201;
});

// Rate a recipe
router.post('/recipes/:recipeId/ratings', async (ctx) => {
    const { recipeId } = ctx.params;
    const { rating } = ctx.request.body;
    if (rating < 1 || rating > 5) {
        ctx.throw(400, 'Invalid input');
    }
    const db = await dbPromise;
    const recipe = await db.get('SELECT * FROM recipes WHERE id = ?', [recipeId]);
    if (!recipe) {
        ctx.throw(404, 'Recipe not found');
    }
    await db.run('INSERT INTO ratings (recipeId, rating) VALUES (?, ?)', [recipeId, rating]);
    ctx.status = 201;
});

// Register routes
app.use(router.routes()).use(router.allowedMethods());

// Initialize database and start server
initDb().then(() => {
    app.listen(5000, () => {
        console.log('Server running on http://0.0.0.0:5000');
    });
}).catch(err => {
    console.error('Database initialization failed:', err);
});