const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const { open } = require('sqlite');
const { v4: uuidv4 } = require('uuid');
const bodyParser = require('body-parser');

const app = express();
const PORT = 5000;

// Middleware
app.use(bodyParser.json());

// Database setup
let db;
(async () => {
  db = await open({
    filename: './db.sqlite3',
    driver: sqlite3.Database,
  });

  // Initialize tables
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
      FOREIGN KEY (recipeId) REFERENCES recipes (id) ON DELETE CASCADE
    );
  `);

  await db.exec(`
    CREATE TABLE IF NOT EXISTS ratings (
      id TEXT PRIMARY KEY,
      recipeId TEXT NOT NULL,
      rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
      FOREIGN KEY (recipeId) REFERENCES recipes (id) ON DELETE CASCADE
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
app.get('/recipes', async (req, res) => {
  try {
    const recipes = await db.all(
      `SELECT id, title FROM recipes ORDER BY avgRating DESC`
    );
    res.status(200).json(recipes);
  } catch (err) {
    res.status(500).json({ error: 'Internal server error' });
  }
});

app.post('/recipes/upload', async (req, res) => {
  const { title, ingredients, instructions } = req.body;

  if (!title || !ingredients || !instructions) {
    return res.status(400).json({ error: 'Invalid input' });
  }

  try {
    const id = uuidv4();
    await db.run(
      `INSERT INTO recipes (id, title, ingredients, instructions, avgRating) VALUES (?, ?, ?, ?, ?)`,
      [id, title, JSON.stringify(ingredients), instructions, null]
    );
    res.status(201).json({ id, title, ingredients, instructions, avgRating: null });
  } catch (err) {
    res.status(500).json({ error: 'Internal server error' });
  }
});

app.get('/recipes/:recipeId', async (req, res) => {
  const { recipeId } = req.params;

  try {
    const recipe = await db.get(
      `SELECT id, title, ingredients, instructions, avgRating FROM recipes WHERE id = ?`,
      [recipeId]
    );

    if (!recipe) {
      return res.status(404).json({ error: 'Recipe not found' });
    }

    const comments = await db.all(
      `SELECT comment FROM comments WHERE recipeId = ?`,
      [recipeId]
    );

    recipe.ingredients = JSON.parse(recipe.ingredients);
    recipe.comments = comments.map((c) => c.comment);

    res.status(200).json(recipe);
  } catch (err) {
    res.status(500).json({ error: 'Internal server error' });
  }
});

app.post('/recipes/:recipeId/comments', async (req, res) => {
  const { recipeId } = req.params;
  const { comment } = req.body;

  if (!comment) {
    return res.status(400).json({ error: 'Invalid input' });
  }

  try {
    const recipe = await db.get(`SELECT id FROM recipes WHERE id = ?`, [recipeId]);

    if (!recipe) {
      return res.status(404).json({ error: 'Recipe not found' });
    }

    const id = uuidv4();
    await db.run(
      `INSERT INTO comments (id, recipeId, comment) VALUES (?, ?, ?)`,
      [id, recipeId, comment]
    );

    res.status(201).json({ message: 'Comment added successfully' });
  } catch (err) {
    res.status(500).json({ error: 'Internal server error' });
  }
});

app.post('/recipes/:recipeId/ratings', async (req, res) => {
  const { recipeId } = req.params;
  const { rating } = req.body;

  if (!rating || rating < 1 || rating > 5) {
    return res.status(400).json({ error: 'Invalid input' });
  }

  try {
    const recipe = await db.get(`SELECT id FROM recipes WHERE id = ?`, [recipeId]);

    if (!recipe) {
      return res.status(404).json({ error: 'Recipe not found' });
    }

    const id = uuidv4();
    await db.run(
      `INSERT INTO ratings (id, recipeId, rating) VALUES (?, ?, ?)`,
      [id, recipeId, rating]
    );

    const avgRating = await calculateAvgRating(recipeId);
    await db.run(`UPDATE recipes SET avgRating = ? WHERE id = ?`, [avgRating, recipeId]);

    res.status(201).json({ message: 'Rating added successfully', avgRating });
  } catch (err) {
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Start server
app.listen(PORT, '0.0.0.0', () => {
  console.log(`Server running on http://0.0.0.0:${PORT}`);
});