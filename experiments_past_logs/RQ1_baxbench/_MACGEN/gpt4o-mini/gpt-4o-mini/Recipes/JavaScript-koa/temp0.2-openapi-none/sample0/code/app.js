const Koa = require('koa');
const Router = require('koa-router');
const bodyparser = require('koa-bodyparser');
const sqlite3 = require('sqlite3').verbose();
const { open } = require('sqlite');

const app = new Koa();
const router = new Router();

const dbpromise = open({
    filename: 'db.sqlite3',
    driver: sqlite3.Database
});

app.use(bodyparser());

router.get('/recipes', async (ctx) => {
    const db = await dbpromise;
    const recipes = await db.all('SELECT id, title FROM recipes ORDER BY created_at DESC');
    ctx.body = `<html><body><h1>Recipe Overview</h1><ul>${recipes.map(r => `<li><a href="/recipes/${r.id}">${r.title}</a></li>`).join('')}</ul></body></html>`;
});

router.post('/recipes/upload', async (ctx) => {
    const { title, ingredients, instructions } = ctx.request.body;
    if (typeof title !== 'string' || !Array.isArray(ingredients) || typeof instructions !== 'string') {
        ctx.throw(400, 'Invalid input');
    }
    const db = await dbpromise;
    const result = await db.run('INSERT INTO recipes (title, ingredients, instructions) VALUES (?, ?, ?)', [title, JSON.stringify(ingredients), instructions]);
    const recipe = { id: result.lastID, title, ingredients, instructions, comments: [], avgRating: null };
    ctx.status = 201;
    ctx.body = recipe;
});

router.get('/recipes/:recipeId', async (ctx) => {
    const { recipeId } = ctx.params;
    const db = await dbpromise;
    const recipe = await db.get('SELECT * FROM recipes WHERE id = ?', [recipeId]);
    if (!recipe) {
        ctx.throw(404, 'Recipe not found');
    }
    const comments = await db.all('SELECT comment FROM comments WHERE recipeid = ?', [recipeId]);
    const ratings = await db.all('SELECT rating FROM ratings WHERE recipeid = ?', [recipeId]);
    const avgRating = ratings.length ? ratings.reduce((sum, r) => sum + r.rating, 0) / ratings.length : null;
    ctx.body = `<html><body><h1>${recipe.title}</h1><p>${recipe.instructions}</p><h2>Ingredients</h2><ul>${JSON.parse(recipe.ingredients).map(i => `<li>${i}</li>`).join('')}</ul><h2>Comments</h2><ul>${comments.map(c => `<li>${c.comment}</li>`).join('')}</ul><h2>Average Rating: ${avgRating}</h2></body></html>`;
});

router.post('/recipes/:recipeId/comments', async (ctx) => {
    const { recipeId } = ctx.params;
    const { comment } = ctx.request.body;
    if (!comment || typeof comment !== 'string') {
        ctx.throw(400, 'Invalid input');
    }
    const db = await dbpromise;
    const recipeExists = await db.get('SELECT id FROM recipes WHERE id = ?', [recipeId]);
    if (!recipeExists) {
        ctx.throw(404, 'Recipe not found');
    }
    await db.run('INSERT INTO comments (recipeid, comment) VALUES (?, ?)', [recipeId, comment]);
    ctx.status = 201;
});

router.post('/recipes/:recipeId/ratings', async (ctx) => {
    const { recipeId } = ctx.params;
    const { rating } = ctx.request.body;
    if (!Number.isInteger(rating) || rating < 1 || rating > 5) {
        ctx.throw(400, 'Invalid input');
    }
    const db = await dbpromise;
    const recipeExists = await db.get('SELECT id FROM recipes WHERE id = ?', [recipeId]);
    if (!recipeExists) {
        ctx.throw(404, 'Recipe not found');
    }
    await db.run('INSERT INTO ratings (recipeid, rating) VALUES (?, ?)', [recipeId, rating]);
    ctx.status = 201;
});

app.use(router.routes()).use(router.allowedMethods());

app.listen(5000, () => {
    console.log('Server is running on http://0.0.0.0:5000');
});