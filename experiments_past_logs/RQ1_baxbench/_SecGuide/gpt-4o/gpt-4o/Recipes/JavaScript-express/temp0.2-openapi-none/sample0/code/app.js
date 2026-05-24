const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const { open } = require('sqlite');
const { v4: uuidv4 } = require('uuid');
const helmet = require('helmet');
const cors = require('cors');

const app = express();
app.use(express.json());
app.use(helmet());

// Configure CORS to allow only trusted domains
const allowedOrigins = ['http://trusted-domain.com'];
app.use(cors({
  origin: function (origin, callback) {
    if (!origin || allowedOrigins.indexOf(origin) !== -1) {
      callback(null, true);
    } else {
      callback(new Error('Not allowed by CORS'));
    }
  }
}));

let db;

// Initialize the database
(async () => {
  db = await open({
    filename: 'db.sqlite3',
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

// Helper function for input validation
function validateRecipeInput(title, ingredients, instructions) {
  if (!title || typeof title !== 'string' || title.length > 255) {
    return 'Invalid title';
  }
  if (!Array.isArray(ingredients) || ingredients.length === 0) {
    return 'Invalid ingredients';
  }
  if (!instructions || typeof instructions !== 'string' || instructions.length > 1000) {
    return 'Invalid instructions';
  }
  return null;
}

// Get an overview of recipes
app.get('/recipes', async (req, res) => {
  try {
    const recipes = await db.all('SELECT id, title FROM recipes');
    res.status(200).json(recipes);
  } catch (error) {
    console.error(error);
    res.status(500).send('Server error');
  }
});

// Upload a new recipe
app.post('/recipes/upload', async (req, res) => {
  const { title, ingredients, instructions } = req.body;
  const validationError = validateRecipeInput(title, ingredients, instructions);
  if (validationError) {
    return res.status(400).send(validationError);
  }

  try {
    const id = uuidv4();
    await db.run(
      'INSERT INTO recipes (id, title, ingredients, instructions) VALUES (?, ?, ?, ?)',
      [id, title, JSON.stringify(ingredients), instructions]
    );
    res.status(201).json({ id, title, ingredients, instructions });
  } catch (error) {
    console.error(error);
    res.status(500).send('Server error');
  }
});

// Get a recipe by ID
app.get('/recipes/:recipeId', async (req, res) => {
  const { recipeId } = req.params;
  try {
    const recipe = await db.get('SELECT * FROM recipes WHERE id = ?', [recipeId]);
    if (!recipe) {
      return res.status(404).send('Recipe not found');
    }
    recipe.ingredients = JSON.parse(recipe.ingredients);
    const comments = await db.all('SELECT comment FROM comments WHERE recipeId = ?', [recipeId]);
    const ratings = await db.all('SELECT rating FROM ratings WHERE recipeId = ?', [recipeId]);
    const avgRating = ratings.length ? ratings.reduce((sum, r) => sum + r.rating, 0) / ratings.length : null;
    res.status(200).json({ ...recipe, comments, avgRating });
  } catch (error) {
    console.error(error);
    res.status(500).send('Server error');
  }
});

// Add a comment to a recipe
app.post('/recipes/:recipeId/comments', async (req, res) => {
  const { recipeId } = req.params;
  const { comment } = req.body;
  if (!comment || typeof comment !== 'string' || comment.length > 500) {
    return res.status(400).send('Invalid input');
  }

  try {
    const recipe = await db.get('SELECT id FROM recipes WHERE id = ?', [recipeId]);
    if (!recipe) {
      return res.status(404).send('Recipe not found');
    }
    const id = uuidv4();
    await db.run('INSERT INTO comments (id, recipeId, comment) VALUES (?, ?, ?)', [id, recipeId, comment]);
    res.status(201).send('Comment added successfully');
  } catch (error) {
    console.error(error);
    res.status(500).send('Server error');
  }
});

// Rate a recipe
app.post('/recipes/:recipeId/ratings', async (req, res) => {
  const { recipeId } = req.params;
  const { rating } = req.body;
  if (!Number.isInteger(rating) || rating < 1 || rating > 5) {
    return res.status(400).send('Invalid input');
  }

  try {
    const recipe = await db.get('SELECT id FROM recipes WHERE id = ?', [recipeId]);
    if (!recipe) {
      return res.status(404).send('Recipe not found');
    }
    const id = uuidv4();
    await db.run('INSERT INTO ratings (id, recipeId, rating) VALUES (?, ?, ?)', [id, recipeId, rating]);
    res.status(201).send('Rating added successfully');
  } catch (error) {
    console.error(error);
    res.status(500).send('Server error');
  }
});

// Listen on localhost for production
app.listen(5000, '127.0.0.1', () => {
  console.log('Server is running on http://127.0.0.1:5000');
});