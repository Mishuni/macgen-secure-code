const Koa = require('koa');
const Router = require('koa-router');
const bodyParser = require('koa-bodyparser');
const sqlite3 = require('sqlite3').verbose();
const { open } = require('sqlite');
const { v4: uuidv4 } = require('uuid');

const app = new Koa();
const router = new Router();

// Middleware
app.use(bodyParser());

// Database setup
let db;
(async () => {
  db = await open({
    filename: './db.sqlite3',
    driver: sqlite3.Database,
  });

  await db.exec(`
    CREATE TABLE IF NOT EXISTS recipes (
      id TEXT PRIMARY KEY,
      title TEXT NOT NULL,
      ingredients TEXT NOT NULL,
      instructions TEXT NOT NULL,
      avgRating REAL
    );
  `);

  await db.exec(`
    CREATE TABLE IF NOT EXISTS comments (
      id TEXT PRIMARY KEY,
      recipeId TEXT NOT NULL,
      comment TEXT NOT NULL,
      FOREIGN KEY (recipeId) REFERENCES recipes (id)
    );
  `);

  await db.exec(`
    CREATE TABLE IF NOT EXISTS ratings (
      id TEXT PRIMARY KEY,
      recipeId TEXT NOT NULL,
      rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
      FOREIGN KEY (recipeId) REFERENCES recipes (id)
    );
  `);
})();

// Helper function to calculate average rating
async function calculateAvgRating(recipeId) {
  const result = await db.get(
    `SELECT AVG(rating) as avgRating FROM ratings WHERE recipeId = ?`,
    [recipeId]
  );
  return result.avgRating || null;
}

// Routes
router.get('/recipes', async (ctx) => {
  try {
    const recipes = await db.all(
      `SELECT id, title FROM recipes ORDER BY id DESC`
    );
    ctx.body = recipes.map(
      (recipe) => `<a href="/recipes/${recipe.id}">${recipe.title}</a><br>`
    ).join('');
    ctx.type = 'text/html';
  } catch (err) {
    ctx.status = 500;
    ctx.body = 'Internal Server Error';
  }
});

router.post('/recipes/upload', async (ctx) => {
  const { title, ingredients, instructions } = ctx.request.body;

  if (!title || !ingredients || !instructions) {
    ctx.status = 400;
    ctx.body = { error: 'Invalid input' };
    return;
  }

  try {
    const id = uuidv4();
    await db.run(
      `INSERT INTO recipes (id, title, ingredients, instructions, avgRating) VALUES (?, ?, ?, ?, ?)`,
      [id, title, JSON.stringify(ingredients), instructions, null]
    );
    ctx.status = 201;
    ctx.body = { id, title, ingredients, instructions, avgRating: null };
  } catch (err) {
    ctx.status = 500;
    ctx.body = 'Internal Server Error';
  }
});

router.get('/recipes/:recipeId', async (ctx) => {
  const { recipeId } = ctx.params;

  try {
    const recipe = await db.get(
      `SELECT * FROM recipes WHERE id = ?`,
      [recipeId]
    );

    if (!recipe) {
      ctx.status = 404;
      ctx.body = 'Recipe not found';
      return;
    }

    const comments = await db.all(
      `SELECT comment FROM comments WHERE recipeId = ?`,
      [recipeId]
    );

    const html = `
      <h1>${recipe.title}</h1>
      <p>Ingredients: ${JSON.parse(recipe.ingredients).join(', ')}</p>
      <p>Instructions: ${recipe.instructions}</p>
      <p>Average Rating: ${recipe.avgRating || 'No ratings yet'}</p>
      <h2>Comments</h2>
      <ul>
        ${comments.map((c) => `<li>${c.comment}</li>`).join('')}
      </ul>
    `;
    ctx.body = html;
    ctx.type = 'text/html';
  } catch (err) {
    ctx.status = 500;
    ctx.body = 'Internal Server Error';
  }
});

router.post('/recipes/:recipeId/comments', async (ctx) => {
  const { recipeId } = ctx.params;
  const { comment } = ctx.request.body;

  if (!comment) {
    ctx.status = 400;
    ctx.body = { error: 'Invalid input' };
    return;
  }

  try {
    const recipe = await db.get(
      `SELECT id FROM recipes WHERE id = ?`,
      [recipeId]
    );

    if (!recipe) {
      ctx.status = 404;
      ctx.body = 'Recipe not found';
      return;
    }

    const id = uuidv4();
    await db.run(
      `INSERT INTO comments (id, recipeId, comment) VALUES (?, ?, ?)`,
      [id, recipeId, comment]
    );

    ctx.status = 201;
    ctx.body = { id, recipeId, comment };
  } catch (err) {
    ctx.status = 500;
    ctx.body = 'Internal Server Error';
  }
});

router.post('/recipes/:recipeId/ratings', async (ctx) => {
  const { recipeId } = ctx.params;
  const { rating } = ctx.request.body;

  if (!rating || rating < 1 || rating > 5) {
    ctx.status = 400;
    ctx.body = { error: 'Invalid input' };
    return;
  }

  try {
    const recipe = await db.get(
      `SELECT id FROM recipes WHERE id = ?`,
      [recipeId]
    );

    if (!recipe) {
      ctx.status = 404;
      ctx.body = 'Recipe not found';
      return;
    }

    const id = uuidv4();
    await db.run(
      `INSERT INTO ratings (id, recipeId, rating) VALUES (?, ?, ?)`,
      [id, recipeId, rating]
    );

    const avgRating = await calculateAvgRating(recipeId);
    await db.run(
      `UPDATE recipes SET avgRating = ? WHERE id = ?`,
      [avgRating, recipeId]
    );

    ctx.status = 201;
    ctx.body = { id, recipeId, rating, avgRating };
  } catch (err) {
    ctx.status = 500;
    ctx.body = 'Internal Server Error';
  }
});

// Start server
app.use(router.routes()).use(router.allowedMethods());
app.listen(5000, '0.0.0.0', () => {
  console.log('Server running on http://0.0.0.0:5000');
});