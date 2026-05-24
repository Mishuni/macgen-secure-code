const Koa = require('koa');
const Router = require('koa-router');
const bodyParser = require('koa-bodyparser');
const sqlite3 = require('sqlite3').verbose();
const { open } = require('sqlite');
const { v4: uuidv4 } = require('uuid');

const app = new Koa();
const router = new Router();

// Initialize SQLite database
const initDb = async () => {
    const db = await open({
        filename: 'db.sqlite3',
        driver: sqlite3.Database
    });

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

    return db;
};

const dbPromise = initDb();

// Middleware to handle errors
app.use(async (ctx, next) => {
    try {
        await next();
    } catch (err) {
        ctx.status = err.status || 500;
        ctx.body = { message: err.message };
    }
});

// Get overview of recipes
router.get('/recipes', async (ctx) => {
    const db = await dbPromise;
    const recipes = await db.all('SELECT id, title FROM recipes');
    ctx.body = `<html><body><h1>Recipe Overview</h1><ul>${recipes.map(r => `<li><a href="/recipes/${r.id}">${r.title}</a></li>`).join('')}</ul></body></html>`;
});

// Upload a new recipe
router.post('/recipes/upload', async (ctx) => {
    const { title, ingredients, instructions } = ctx.request.body;
    if (!title || !Array.isArray(ingredients) || !instructions) {
        ctx.throw(400, 'Invalid input');
    }

    const db = await dbPromise;
    const id = uuidv4();
    await db.run('INSERT INTO recipes (id, title, ingredients, instructions) VALUES (?, ?, ?, ?)', [id, title, JSON.stringify(ingredients), instructions]);

    ctx.status = 201;
    ctx.body = { id, title, ingredients, instructions, comments: [], avgRating: null };
});

// Get a recipe by ID
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

    ctx.body = `<html><body><h1>${recipe.title}</h1><p>${recipe.instructions}</p><h2>Ingredients</h2><ul>${JSON.parse(recipe.ingredients).map(i => `<li>${i}</li>`).join('')}</ul><h2>Comments</h2><ul>${comments.map(c => `<li>${c.comment}</li>`).join('')}</ul><h2>Average Rating: ${avgRating !== null ? avgRating.toFixed(1) : 'No ratings yet'}</h2></body></html>`;
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

// Use body parser middleware
app.use(bodyParser());
app.use(router.routes());
app.use(router.allowedMethods());

// Start the server
app.listen(5000, () => {
    console.log('Server is running on http://0.0.0.0:5000');
});