import fastify from 'fastify';
import { v4 as uuidv4 } from 'uuid';
import sqlite3 from 'sqlite3';
import { open } from 'sqlite';

// Initialize Fastify
const app = fastify();

// Open SQLite database
let db;
(async () => {
  db = await open({
    filename: './db.sqlite3',
    driver: sqlite3.Database
  });

  // Create tables if they don't exist
  await db.exec(`
    CREATE TABLE IF NOT EXISTS recipes (
      id TEXT PRIMARY KEY,
      title TEXT NOT NULL,
      ingredients TEXT NOT NULL,
      instructions TEXT NOT NULL,
      avgRating REAL
    );
    CREATE TABLE IF NOT EXISTS comments (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      recipeId TEXT NOT NULL,
      comment TEXT NOT NULL,
      FOREIGN KEY (recipeId) REFERENCES recipes(id)
    );
    CREATE TABLE IF NOT EXISTS ratings (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      recipeId TEXT NOT NULL,
      rating INTEGER NOT NULL,
      FOREIGN KEY (recipeId) REFERENCES recipes(id)
    );
  `);
})();

// Helper function to calculate average rating
async function calculateAvgRating(recipeId) {
  const ratings = await db.all('SELECT rating FROM ratings WHERE recipeId = ?', recipeId);
  if (ratings.length === 0) return null;
  const avgRating = ratings.reduce((sum, r) => sum + r.rating, 0) / ratings.length;
  await db.run('UPDATE recipes SET avgRating = ? WHERE id = ?', avgRating, recipeId);
  return avgRating;
}

// Routes
app.get('/recipes', async (request, reply) => {
  try {
    const recipes = await db.all('SELECT id, title FROM recipes');
    const html = recipes.map(r => `<a href="/recipes/${r.id}">${r.title}</a>`).join('<br>');
    reply.type('text/html').send(html);
  } catch (err) {
    reply.code(500).send('Server error');
  }
});

app.post('/recipes/upload', async (request, reply) => {
  const { title, ingredients, instructions } = request.body;
  if (!title || !Array.isArray(ingredients) || !instructions) {
    return reply.code(400).send('Invalid input');
  }
  const id = uuidv4();
  try {
    await db.run('INSERT INTO recipes (id, title, ingredients, instructions) VALUES (?, ?, ?, ?)', id, title, JSON.stringify(ingredients), instructions);
    reply.code(201).send({ id, title, ingredients, instructions, comments: [], avgRating: null });
  } catch (err) {
    reply.code(500).send('Server error');
  }
});

app.get('/recipes/:recipeId', async (request, reply) => {
  const { recipeId } = request.params;
  try {
    const recipe = await db.get('SELECT * FROM recipes WHERE id = ?', recipeId);
    if (!recipe) return reply.code(404).send('Recipe not found');
    const comments = await db.all('SELECT comment FROM comments WHERE recipeId = ?', recipeId);
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
    reply.code(500).send('Server error');
  }
});

app.post('/recipes/:recipeId/comments', async (request, reply) => {
  const { recipeId } = request.params;
  const { comment } = request.body;
  if (!comment) return reply.code(400).send('Invalid input');
  try {
    const recipe = await db.get('SELECT id FROM recipes WHERE id = ?', recipeId);
    if (!recipe) return reply.code(404).send('Recipe not found');
    await db.run('INSERT INTO comments (recipeId, comment) VALUES (?, ?)', recipeId, comment);
    reply.code(201).send('Comment added successfully');
  } catch (err) {
    reply.code(500).send('Server error');
  }
});

app.post('/recipes/:recipeId/ratings', async (request, reply) => {
  const { recipeId } = request.params;
  const { rating } = request.body;
  if (!rating || typeof rating !== 'number' || rating < 1 || rating > 5) return reply.code(400).send('Invalid input');
  try {
    const recipe = await db.get('SELECT id FROM recipes WHERE id = ?', recipeId);
    if (!recipe) return reply.code(404).send('Recipe not found');
    await db.run('INSERT INTO ratings (recipeId, rating) VALUES (?, ?)', recipeId, rating);
    const avgRating = await calculateAvgRating(recipeId);
    reply.code(201).send({ avgRating });
  } catch (err) {
    reply.code(500).send('Server error');
  }
});

// Start server
app.listen({ port: 5000, host: '0.0.0.0' }, (err, address) => {
  if (err) {
    console.error(err);
    process.exit(1);
  }
  console.log(`Server listening at ${address}`);
});