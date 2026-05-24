const Koa = require('koa');
const Router = require('koa-router');
const bodyParser = require('koa-bodyparser');
const sqlite3 = require('sqlite3').verbose();
const { open } = require('sqlite');
const uuid = require('uuid');

const app = new Koa();
const router = new Router();

// Initialize SQLite database
let db;
(async () => {
  db = await open({
    filename: './db.sqlite3',
    driver: sqlite3.Database
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
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      recipeId TEXT NOT NULL,
      comment TEXT NOT NULL,
      FOREIGN KEY(recipeId) REFERENCES recipes(id)
    );
  `);

  await db.exec(`
    CREATE TABLE IF NOT EXISTS ratings (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      recipeId TEXT NOT NULL,
      rating INTEGER NOT NULL,
      FOREIGN KEY(recipeId) REFERENCES recipes(id)
    );
  `);
})();

// Middleware
app.use(bodyParser());

// Helper function for input validation
function validateRecipeInput(title, ingredients, instructions) {
  if (typeof title !== 'string' || title.length === 0 || title.length > 255) return false;
  if (!Array.isArray(ingredients) || ingredients.length === 0 || ingredients.some(ing => typeof ing !== 'string')) return false;
  if (typeof instructions !== 'string' || instructions.length === 0) return false;
  return true;
}

// Routes
router.get('/recipes', async (ctx) => {
  try {
    const recipes = await db.all('SELECT id, title FROM recipes');
    ctx.body = recipes.map(recipe => `<a href="/recipes/${recipe.id}">${recipe.title}</a>`).join('<br>');
    ctx.type = 'text/html';
  } catch (err) {
    ctx.status = 500;
    ctx.body = 'Server error';
  }
});

router.post('/recipes/upload', async (ctx) => {
  const { title, ingredients, instructions } = ctx.request.body;
  if (!validateRecipeInput(title, ingredients, instructions)) {
    ctx.status = 400;
    ctx.body = 'Invalid input';
    return;
  }

  const id = uuid.v4();
  try {
    await db.run('INSERT INTO recipes (id, title, ingredients, instructions) VALUES (?, ?, ?, ?)', 
      id, title, JSON.stringify(ingredients), instructions);
    ctx.status = 201;
    ctx.body = { id, title, ingredients, instructions, comments: [], avgRating: null };
  } catch (err) {
    ctx.status = 500;
    ctx.body = 'Server error';
  }
});

router.get('/recipes/:recipeId', async (ctx) => {
  const { recipeId } = ctx.params;
  try {
    const recipe = await db.get('SELECT * FROM recipes WHERE id = ?', recipeId);
    if (!recipe) {
      ctx.status = 404;
      ctx.body = 'Recipe not found';
      return;
    }

    const comments = await db.all('SELECT comment FROM comments WHERE recipeId = ?', recipeId);
    const ratings = await db.all('SELECT rating FROM ratings WHERE recipeId = ?', recipeId);
    const avgRating = ratings.length ? (ratings.reduce((sum, r) => sum + r.rating, 0) / ratings.length) : null;

    ctx.body = `
      <h1>${recipe.title}</h1>
      <p>Ingredients: ${JSON.parse(recipe.ingredients).join(', ')}</p>
      <p>Instructions: ${recipe.instructions}</p>
      <p>Average Rating: ${avgRating || 'No ratings yet'}</p>
      <h2>Comments</h2>
      <ul>${comments.map(c => `<li>${c.comment}</li>`).join('')}</ul>
    `;
    ctx.type = 'text/html';
  } catch (err) {
    ctx.status = 500;
    ctx.body = 'Server error';
  }
});

router.post('/recipes/:recipeId/comments', async (ctx) => {
  const { recipeId } = ctx.params;
  const { comment } = ctx.request.body;
  if (typeof comment !== 'string' || comment.length === 0) {
    ctx.status = 400;
    ctx.body = 'Invalid input';
    return;
  }

  try {
    const recipe = await db.get('SELECT id FROM recipes WHERE id = ?', recipeId);
    if (!recipe) {
      ctx.status = 404;
      ctx.body = 'Recipe not found';
      return;
    }

    await db.run('INSERT INTO comments (recipeId, comment) VALUES (?, ?)', recipeId, comment);
    ctx.status = 201;
    ctx.body = 'Comment added successfully';
  } catch (err) {
    ctx.status = 500;
    ctx.body = 'Server error';
  }
});

router.post('/recipes/:recipeId/ratings', async (ctx) => {
  const { recipeId } = ctx.params;
  const { rating } = ctx.request.body;
  if (typeof rating !== 'number' || rating < 1 || rating > 5) {
    ctx.status = 400;
    ctx.body = 'Invalid input';
    return;
  }

  try {
    const recipe = await db.get('SELECT id FROM recipes WHERE id = ?', recipeId);
    if (!recipe) {
      ctx.status = 404;
      ctx.body = 'Recipe not found';
      return;
    }

    await db.run('INSERT INTO ratings (recipeId, rating) VALUES (?, ?)', recipeId, rating);
    ctx.status = 201;
    ctx.body = 'Rating added successfully';
  } catch (err) {
    ctx.status = 500;
    ctx.body = 'Server error';
  }
});

// Start server
app.use(router.routes()).use(router.allowedMethods());
app.listen(5000, () => {
  console.log('Server running on http://0.0.0.0:5000');
});