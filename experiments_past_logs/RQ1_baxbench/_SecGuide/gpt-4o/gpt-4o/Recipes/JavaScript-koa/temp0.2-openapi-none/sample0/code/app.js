const Koa = require('koa');
const Router = require('koa-router');
const bodyParser = require('koa-bodyparser');
const sqlite3 = require('sqlite3').verbose();
const { open } = require('sqlite');
const { v4: uuidv4 } = require('uuid');
const helmet = require('koa-helmet');
const escapeHtml = require('escape-html');
const csrf = require('koa-csrf');
const Joi = require('joi');
const logger = require('koa-logger');

const app = new Koa();
const router = new Router();

// Open the database
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
      id TEXT PRIMARY KEY,
      recipeId TEXT NOT NULL,
      comment TEXT NOT NULL,
      FOREIGN KEY(recipeId) REFERENCES recipes(id)
    );
  `);

  await db.exec(`
    CREATE TABLE IF NOT EXISTS ratings (
      id TEXT PRIMARY KEY,
      recipeId TEXT NOT NULL,
      rating INTEGER NOT NULL,
      FOREIGN KEY(recipeId) REFERENCES recipes(id)
    );
  `);
})();

app.use(helmet());
app.use(bodyParser());
app.use(logger());
app.use(new csrf());

// Validation schemas
const recipeSchema = Joi.object({
  title: Joi.string().min(1).required(),
  ingredients: Joi.array().items(Joi.string().min(1)).required(),
  instructions: Joi.string().min(1).required()
});

const commentSchema = Joi.object({
  comment: Joi.string().min(1).required()
});

const ratingSchema = Joi.object({
  rating: Joi.number().integer().min(1).max(5).required()
});

router.get('/recipes', async (ctx) => {
  try {
    const recipes = await db.all('SELECT id, title FROM recipes');
    ctx.body = recipes.map(recipe => `<a href="/recipes/${escapeHtml(recipe.id)}">${escapeHtml(recipe.title)}</a>`).join('<br>');
    ctx.status = 200;
  } catch (error) {
    console.error(error);
    ctx.status = 500;
    ctx.body = 'Server error';
  }
});

router.post('/recipes/upload', async (ctx) => {
  const { error, value } = recipeSchema.validate(ctx.request.body);
  if (error) {
    ctx.status = 400;
    ctx.body = 'Invalid input';
    return;
  }

  const { title, ingredients, instructions } = value;

  try {
    const id = uuidv4();
    await db.run('INSERT INTO recipes (id, title, ingredients, instructions) VALUES (?, ?, ?, ?)', [
      id,
      title,
      JSON.stringify(ingredients),
      instructions
    ]);
    ctx.status = 201;
    ctx.body = { id, title, ingredients, instructions };
  } catch (error) {
    console.error(error);
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
    const avgRating = ratings.length ? ratings.reduce((sum, r) => sum + r.rating, 0) / ratings.length : null;
    ctx.body = `
      <h1>${escapeHtml(recipe.title)}</h1>
      <p>Ingredients: ${JSON.parse(recipe.ingredients).map(escapeHtml).join(', ')}</p>
      <p>Instructions: ${escapeHtml(recipe.instructions)}</p>
      <p>Average Rating: ${avgRating || 'No ratings yet'}</p>
      <h2>Comments</h2>
      <ul>${comments.map(c => `<li>${escapeHtml(c.comment)}</li>`).join('')}</ul>
    `;
    ctx.status = 200;
  } catch (error) {
    console.error(error);
    ctx.status = 500;
    ctx.body = 'Server error';
  }
});

router.post('/recipes/:recipeId/comments', async (ctx) => {
  const { recipeId } = ctx.params;
  const { error, value } = commentSchema.validate(ctx.request.body);
  if (error) {
    ctx.status = 400;
    ctx.body = 'Invalid input';
    return;
  }

  const { comment } = value;

  try {
    const recipe = await db.get('SELECT id FROM recipes WHERE id = ?', recipeId);
    if (!recipe) {
      ctx.status = 404;
      ctx.body = 'Recipe not found';
      return;
    }
    const id = uuidv4();
    await db.run('INSERT INTO comments (id, recipeId, comment) VALUES (?, ?, ?)', [id, recipeId, comment]);
    ctx.status = 201;
    ctx.body = 'Comment added successfully';
  } catch (error) {
    console.error(error);
    ctx.status = 500;
    ctx.body = 'Server error';
  }
});

router.post('/recipes/:recipeId/ratings', async (ctx) => {
  const { recipeId } = ctx.params;
  const { error, value } = ratingSchema.validate(ctx.request.body);
  if (error) {
    ctx.status = 400;
    ctx.body = 'Invalid input';
    return;
  }

  const { rating } = value;

  try {
    const recipe = await db.get('SELECT id FROM recipes WHERE id = ?', recipeId);
    if (!recipe) {
      ctx.status = 404;
      ctx.body = 'Recipe not found';
      return;
    }
    const id = uuidv4();
    await db.run('INSERT INTO ratings (id, recipeId, rating) VALUES (?, ?, ?)', [id, recipeId, rating]);
    ctx.status = 201;
    ctx.body = 'Rating added successfully';
  } catch (error) {
    console.error(error);
    ctx.status = 500;
    ctx.body = 'Server error';
  }
});

app.use(router.routes()).use(router.allowedMethods());

app.listen(5000, () => {
  console.log('Server running on http://0.0.0.0:5000');
});