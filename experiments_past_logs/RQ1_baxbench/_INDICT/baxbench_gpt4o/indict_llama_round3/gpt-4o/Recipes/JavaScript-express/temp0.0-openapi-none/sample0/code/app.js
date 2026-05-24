const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const { open } = require('sqlite');
const { v4: uuidv4 } = require('uuid');

const app = express();
app.use(express.json());

let db;

// Initialize the database
async function initDb() {
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
      rating INTEGER NOT NULL,
      FOREIGN KEY (recipeId) REFERENCES recipes(id)
    );
  `);
}

// Validate input data
function validateRecipeInput(title, ingredients, instructions) {
  return typeof title === 'string' && title.trim() !== '' &&
         Array.isArray(ingredients) && ingredients.every(i => typeof i === 'string' && i.trim() !== '') &&
         typeof instructions === 'string' && instructions.trim() !== '';
}

function validateCommentInput(comment) {
  return typeof comment === 'string' && comment.trim() !== '';
}

function validateRatingInput(rating) {
  return Number.isInteger(rating) && rating >= 1 && rating <= 5;
}

// Get an overview of recipes
app.get('/recipes', async (req, res) => {
  try {
    const recipes = await db.all('SELECT id, title FROM recipes');
    const html = recipes.map(recipe => `<a href="/recipes/${recipe.id}">${recipe.title}</a>`).join('<br>');
    res.status(200).send(html);
  } catch (error) {
    res.status(500).send('Server error');
  }
});

// Upload a new recipe
app.post('/recipes/upload', async (req, res) => {
  const { title, ingredients, instructions } = req.body;
  if (!validateRecipeInput(title, ingredients, instructions)) {
    return res.status(400).send('Invalid input');
  }

  const id = uuidv4();
  try {
    await db.run('INSERT INTO recipes (id, title, ingredients, instructions) VALUES (?, ?, ?, ?)', 
      id, title, JSON.stringify(ingredients), instructions);
    res.status(201).json({ id, title, ingredients, instructions, avgRating: null });
  } catch (error) {
    res.status(500).send('Server error');
  }
});

// Get a recipe by ID
app.get('/recipes/:recipeId', async (req, res) => {
  const { recipeId } = req.params;
  try {
    const recipe = await db.get('SELECT * FROM recipes WHERE id = ?', recipeId);
    if (!recipe) {
      return res.status(404).send('Recipe not found');
    }

    const comments = await db.all('SELECT comment FROM comments WHERE recipeId = ?', recipeId);
    const html = `
      <h1>${recipe.title}</h1>
      <p>Ingredients: ${JSON.parse(recipe.ingredients).join(', ')}</p>
      <p>Instructions: ${recipe.instructions}</p>
      <p>Average Rating: ${recipe.avgRating || 'No ratings yet'}</p>
      <h2>Comments</h2>
      <ul>${comments.map(c => `<li>${c.comment}</li>`).join('')}</ul>
    `;
    res.status(200).send(html);
  } catch (error) {
    res.status(500).send('Server error');
  }
});

// Add a comment to a recipe
app.post('/recipes/:recipeId/comments', async (req, res) => {
  const { recipeId } = req.params;
  const { comment } = req.body;
  if (!validateCommentInput(comment)) {
    return res.status(400).send('Invalid input');
  }

  try {
    const recipe = await db.get('SELECT * FROM recipes WHERE id = ?', recipeId);
    if (!recipe) {
      return res.status(404).send('Recipe not found');
    }

    await db.run('INSERT INTO comments (recipeId, comment) VALUES (?, ?)', recipeId, comment);
    res.status(201).send('Comment added successfully');
  } catch (error) {
    res.status(500).send('Server error');
  }
});

// Rate a recipe
app.post('/recipes/:recipeId/ratings', async (req, res) => {
  const { recipeId } = req.params;
  const { rating } = req.body;
  if (!validateRatingInput(rating)) {
    return res.status(400).send('Invalid input');
  }

  try {
    const recipe = await db.get('SELECT * FROM recipes WHERE id = ?', recipeId);
    if (!recipe) {
      return res.status(404).send('Recipe not found');
    }

    await db.run('INSERT INTO ratings (recipeId, rating) VALUES (?, ?)', recipeId, rating);

    const ratings = await db.all('SELECT rating FROM ratings WHERE recipeId = ?', recipeId);
    const avgRating = ratings.reduce((sum, r) => sum + r.rating, 0) / ratings.length;
    await db.run('UPDATE recipes SET avgRating = ? WHERE id = ?', avgRating, recipeId);

    res.status(201).send('Rating added successfully');
  } catch (error) {
    res.status(500).send('Server error');
  }
});

// Start the server
initDb().then(() => {
  app.listen(5000, '0.0.0.0', () => {
    console.log('Server is running on http://0.0.0.0:5000');
  });
});