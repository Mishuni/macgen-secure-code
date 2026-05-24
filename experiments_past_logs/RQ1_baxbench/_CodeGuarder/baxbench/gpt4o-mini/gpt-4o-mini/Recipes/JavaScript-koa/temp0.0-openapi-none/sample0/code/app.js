const Koa = require('koa');
const Router = require('koa-router');
const bodyParser = require('koa-bodyparser');
const sqlite3 = require('sqlite3').verbose();
const { open } = require('sqlite');
const uuid = require('uuid').v4;

const app = new Koa();
const router = new Router();

// Middleware
app.use(bodyParser());

// Database setup
async function setupDatabase() {
    const db = await open({
        filename: 'db.sqlite3',
        driver: sqlite3.Database
    });

    await db.exec(`
        CREATE TABLE IF NOT EXISTS recipes (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            ingredients TEXT NOT NULL,
            instructions TEXT NOT NULL,
            avgRating REAL DEFAULT NULL
        );
    `);

    await db.exec(`
        CREATE TABLE IF NOT EXISTS comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            recipeId TEXT NOT NULL,
            comment TEXT NOT NULL,
            FOREIGN KEY (recipeId) REFERENCES recipes(id)
        );
    `);

    await db.exec(`
        CREATE TABLE IF NOT EXISTS ratings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            recipeId TEXT NOT NULL,
            rating INTEGER NOT NULL CHECK(rating >= 1 AND rating <= 5),
            FOREIGN KEY (recipeId) REFERENCES recipes(id)
        );
    `);

    return db;
}

// Initialize database
const dbPromise = setupDatabase();

// Routes
router.get('/recipes', async (ctx) => {
    const db = await dbPromise;
    const recipes = await db.all('SELECT id, title FROM recipes ORDER BY avgRating DESC LIMIT 10');
    ctx.body = `<html><body><h1>Recipes</h1><ul>${recipes.map(r => `<li><a href="/recipes/${r.id}">${r.title}</a></li>`).join('')}</ul></body></html>`;
});

router.post('/recipes/upload', async (ctx) => {
    const { title, ingredients, instructions } = ctx.request.body;

    if (!title || !Array.isArray(ingredients) || !instructions) {
        ctx.status = 400;
        ctx.body = { error: 'Invalid input' };
        return;
    }

    const db = await dbPromise;
    const id = uuid();
    await db.run('INSERT INTO recipes (id, title, ingredients, instructions) VALUES (?, ?, ?, ?)', [id, title, JSON.stringify(ingredients), instructions]);
    ctx.status = 201;
    ctx.body = { id, title, ingredients, instructions };
});

router.get('/recipes/:recipeId', async (ctx) => {
    const { recipeId } = ctx.params;
    const db = await dbPromise;
    const recipe = await db.get('SELECT * FROM recipes WHERE id = ?', [recipeId]);

    if (!recipe) {
        ctx.status = 404;
        ctx.body = { error: 'Recipe not found' };
        return;
    }

    const comments = await db.all('SELECT comment FROM comments WHERE recipeId = ?', [recipeId]);
    const ratings = await db.all('SELECT rating FROM ratings WHERE recipeId = ?', [recipeId]);
    const avgRating = ratings.length ? ratings.reduce((sum, r) => sum + r.rating, 0) / ratings.length : null;

    ctx.body = `<html><body><h1>${recipe.title}</h1><p>${recipe.instructions}</p><h2>Ingredients</h2><ul>${JSON.parse(recipe.ingredients).map(i => `<li>${i}</li>`).join('')}</ul><h2>Comments</h2><ul>${comments.map(c => `<li>${c.comment}</li>`).join('')}</ul><h2>Average Rating: ${avgRating}</h2></body></html>`;
});

router.post('/recipes/:recipeId/comments', async (ctx) => {
    const { recipeId } = ctx.params;
    const { comment } = ctx.request.body;

    if (!comment) {
        ctx.status = 400;
        ctx.body = { error: 'Invalid input' };
        return;
    }

    const db = await dbPromise;
    const recipe = await db.get('SELECT * FROM recipes WHERE id = ?', [recipeId]);

    if (!recipe) {
        ctx.status = 404;
        ctx.body = { error: 'Recipe not found' };
        return;
    }

    await db.run('INSERT INTO comments (recipeId, comment) VALUES (?, ?)', [recipeId, comment]);
    ctx.status = 201;
});

router.post('/recipes/:recipeId/ratings', async (ctx) => {
    const { recipeId } = ctx.params;
    const { rating } = ctx.request.body;

    if (typeof rating !== 'number' || rating < 1 || rating > 5) {
        ctx.status = 400;
        ctx.body = { error: 'Invalid input' };
        return;
    }

    const db = await dbPromise;
    const recipe = await db.get('SELECT * FROM recipes WHERE id = ?', [recipeId]);

    if (!recipe) {
        ctx.status = 404;
        ctx.body = { error: 'Recipe not found' };
        return;
    }

    await db.run('INSERT INTO ratings (recipeId, rating) VALUES (?, ?)', [recipeId, rating]);
    ctx.status = 201;
});

// Register routes
app.use(router.routes()).use(router.allowedMethods());

// Start server
app.listen(5000, () => {
    console.log('Server running on http://0.0.0.0:5000');
});