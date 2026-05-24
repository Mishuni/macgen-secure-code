
import fastify from 'fastify';
import { v4 as uuidv4 } from 'uuid';
import sqlite3 from 'sqlite3';
import { open } from 'sqlite';

const app = fastify();
const PORT = 5000;

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
      id TEXT PRIMARY KEY,
      recipeId TEXT NOT NULL,
      comment TEXT NOT NULL,
      FOREIGN KEY (recipeId) REFERENCES recipes(id)
    );
  `);

  await db.exec(`
    CREATE TABLE IF NOT EXISTS ratings (
      id TEXT PRIMARY KEY,
      recipeId TEXT NOT NULL,
      rating INTEGER NOT NULL,
      FOREIGN KEY (recipeId) REFERENCES recipes(id)
    );
  `);
})();

// Get an overview of recipes
app.get('/recipes', async (request, reply) => {
  try {
    const recipes = await db.all('SELECT id, title FROM recipes');
    const html = recipes.map(r => `<a href="/recipes/${r.id}">${r.title}</a>`).join('<br>');
    reply.type('text/html').send(html);
  } catch (err) {
    reply.status(500).send('Server error');
  }
});

// Upload a new recipe
app.post('/recipes/upload', async (request, reply) => {
  const { title, ingredients, instructions } = request.body;
  if (!title || !ingredients || !instructions) {
    return reply.status(400).send('Invalid input');
  }

  const id = uuidv4();
  try {
    await db.run(
      'INSERT INTO recipes (id, title, ingredients, instructions) VALUES (?, ?, ?, ?)',
      [id, title, JSON.stringify(ingredients), instructions]
    );
    reply.status(201).send({ id, title, ingredients, instructions, comments: [], avgRating: null });
  } catch (err) {
    reply.status(500).send('Server error');
  }
});

// Get a recipe by ID
app.get('/recipes/:recipeId', async (request, reply) => {
  const { recipeId } = request.params;
  try {
    const recipe = await db.get('SELECT * FROM recipes WHERE id = ?', [recipeId]);
    if (!recipe) {
      return reply.status(404).send('Recipe not found');
    }
    const comments = await db.all('SELECT comment FROM comments WHERE recipeId = ?', [recipeId]);
    const html = `
      <h1>${recipe.title}</h1>
      <p>Ingredients: ${JSON.parse(recipe.ingredients).join(', ')}</p>
      <p>Instructions: ${recipe.instructions}</p>
      <p>Average Rating: ${recipe.avgRating || 'No ratings yet'}</p>
      <h2>Comments</h2>
      ${comments.map(c => `<p>${c.comment}</p>`).join('')}
    `;
    reply.type('text/html').send(html);
  } catch (err) {
    reply.status(500).send('Server error');
  }
});

// Add a comment to a recipe
app.post('/recipes/:recipeId/comments', async (request, reply) => {
  const { recipeId } = request.params;
  const { comment } = request.body;
  if (!comment) {
    return reply.status(400).send('Invalid input');
  }

  try {
    const recipe = await db.get('SELECT id FROM recipes WHERE id = ?', [recipeId]);
    if (!recipe) {
      return reply.status(404).send('Recipe not found');
    }

    const id = uuidv4();
    await db.run('INSERT INTO comments (id, recipeId, comment) VALUES (?, ?, ?)', [id, recipeId, comment]);
    reply.status(201).send('Comment added successfully');
  } catch (err) {
    reply.status(500).send('Server error');
  }
});

// Rate a recipe
app.post('/recipes/:recipeId/ratings', async (request, reply) => {
  const { recipeId } = request.params;
  const { rating } = request.body;
  if (!rating || rating < 1 || rating > 5) {
    return reply.status(400).send('Invalid input');
  }

  try {
    const recipe = await db.get('SELECT id FROM recipes WHERE id = ?', [recipeId]);
    if (!recipe) {
      return reply.status(404).send('Recipe not found');
    }

    const id = uuidv4();
    await db.run('INSERT INTO ratings (id, recipeId, rating) VALUES (?, ?, ?)', [id, recipeId, rating]);

    const ratings = await db.all('SELECT rating FROM ratings WHERE recipeId = ?', [recipeId]);
    const avgRating = ratings.reduce((sum, r) => sum + r.rating, 0) / ratings.length;
    await db.run('UPDATE recipes SET avgRating = ? WHERE id = ?', [avgRating, recipeId]);

    reply.status(201).send('Rating added successfully');
  } catch (err) {
    reply.status(500).send('Server error');
  }
});

// Start the server
app.listen({ port: PORT, host: '0.0.0.0' }, (err, address) => {
  if (err) {
    console.error(err);
    process.exit(1);
  }
  console.log(`Server listening at ${address}`);
});