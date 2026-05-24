import fastify from 'fastify';
import sqlite3 from 'sqlite3';
import { v4 as uuidv4 } from 'uuid';
import escapeHtml from 'escape-html';

// Initialize Fastify app
const app = fastify();

// Initialize SQLite database
const db = new sqlite3.Database('db.sqlite3');

// Create tables if they don't exist
db.serialize(() => {
  db.run(`CREATE TABLE IF NOT EXISTS recipes (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    ingredients TEXT NOT NULL,
    instructions TEXT NOT NULL,
    avgRating REAL
  )`);

  db.run(`CREATE TABLE IF NOT EXISTS comments (
    id TEXT PRIMARY KEY,
    recipeId TEXT NOT NULL,
    comment TEXT NOT NULL,
    FOREIGN KEY(recipeId) REFERENCES recipes(id)
  )`);

  db.run(`CREATE TABLE IF NOT EXISTS ratings (
    id TEXT PRIMARY KEY,
    recipeId TEXT NOT NULL,
    rating INTEGER NOT NULL,
    FOREIGN KEY(recipeId) REFERENCES recipes(id)
  )`);
});

// Helper function to calculate average rating
function calculateAvgRating(recipeId, callback) {
  db.all(`SELECT rating FROM ratings WHERE recipeId = ?`, [recipeId], (err, rows) => {
    if (err) {
      callback(err);
      return;
    }
    const ratings = rows.map(row => row.rating);
    const avgRating = ratings.length ? ratings.reduce((a, b) => a + b, 0) / ratings.length : null;
    callback(null, avgRating);
  });
}

// Validate input data
function validateInput(data, constraints) {
  for (const [key, constraint] of Object.entries(constraints)) {
    if (!data[key] || typeof data[key] !== constraint.type || (constraint.maxLength && data[key].length > constraint.maxLength)) {
      return false;
    }
  }
  return true;
}

// Get an overview of recipes
app.get('/recipes', (request, reply) => {
  db.all(`SELECT id, title FROM recipes`, (err, rows) => {
    if (err) {
      reply.code(500).send('Server error');
      return;
    }
    const html = rows.map(row => `<a href="/recipes/${row.id}">${escapeHtml(row.title)}</a>`).join('<br>');
    reply.type('text/html').send(html);
  });
});

// Upload a new recipe
app.post('/recipes/upload', (request, reply) => {
  const { title, ingredients, instructions } = request.body;
  const constraints = {
    title: { type: 'string', maxLength: 255 },
    ingredients: { type: 'string', maxLength: 1000 },
    instructions: { type: 'string', maxLength: 2000 }
  };
  if (!validateInput({ title, ingredients, instructions }, constraints)) {
    reply.code(400).send('Invalid input');
    return;
  }
  const id = uuidv4();
  db.run(`INSERT INTO recipes (id, title, ingredients, instructions) VALUES (?, ?, ?, ?)`, [id, title, JSON.stringify(ingredients), instructions], (err) => {
    if (err) {
      reply.code(500).send('Server error');
      return;
    }
    reply.code(201).send({ id, title, ingredients, instructions, avgRating: null });
  });
});

// Get a recipe by ID
app.get('/recipes/:recipeId', (request, reply) => {
  const { recipeId } = request.params;
  db.get(`SELECT * FROM recipes WHERE id = ?`, [recipeId], (err, recipe) => {
    if (err || !recipe) {
      reply.code(404).send('Recipe not found');
      return;
    }
    db.all(`SELECT comment FROM comments WHERE recipeId = ?`, [recipeId], (err, comments) => {
      if (err) {
        reply.code(500).send('Server error');
        return;
      }
      const commentsHtml = comments.map(c => `<p>${escapeHtml(c.comment)}</p>`).join('');
      const html = `<h1>${escapeHtml(recipe.title)}</h1><p>${escapeHtml(recipe.instructions)}</p><h2>Comments</h2>${commentsHtml}`;
      reply.type('text/html').send(html);
    });
  });
});

// Add a comment to a recipe
app.post('/recipes/:recipeId/comments', (request, reply) => {
  const { recipeId } = request.params;
  const { comment } = request.body;
  if (!comment || typeof comment !== 'string' || comment.length > 500) {
    reply.code(400).send('Invalid input');
    return;
  }
  db.get(`SELECT id FROM recipes WHERE id = ?`, [recipeId], (err, recipe) => {
    if (err || !recipe) {
      reply.code(404).send('Recipe not found');
      return;
    }
    const id = uuidv4();
    db.run(`INSERT INTO comments (id, recipeId, comment) VALUES (?, ?, ?)`, [id, recipeId, comment], (err) => {
      if (err) {
        reply.code(500).send('Server error');
        return;
      }
      reply.code(201).send('Comment added successfully');
    });
  });
});

// Rate a recipe
app.post('/recipes/:recipeId/ratings', (request, reply) => {
  const { recipeId } = request.params;
  const { rating } = request.body;
  if (!rating || typeof rating !== 'number' || rating < 1 || rating > 5) {
    reply.code(400).send('Invalid input');
    return;
  }
  db.get(`SELECT id FROM recipes WHERE id = ?`, [recipeId], (err, recipe) => {
    if (err || !recipe) {
      reply.code(404).send('Recipe not found');
      return;
    }
    const id = uuidv4();
    db.run(`INSERT INTO ratings (id, recipeId, rating) VALUES (?, ?, ?)`, [id, recipeId, rating], (err) => {
      if (err) {
        reply.code(500).send('Server error');
        return;
      }
      calculateAvgRating(recipeId, (err, avgRating) => {
        if (err) {
          reply.code(500).send('Server error');
          return;
        }
        db.run(`UPDATE recipes SET avgRating = ? WHERE id = ?`, [avgRating, recipeId], (err) => {
          if (err) {
            reply.code(500).send('Server error');
            return;
          }
          reply.code(201).send('Rating added successfully');
        });
      });
    });
  });
});

// Start the server
app.listen({ port: 5000, host: '0.0.0.0' }, (err, address) => {
  if (err) {
    console.error(err);
    process.exit(1);
  }
  console.log(`Server listening at ${address}`);
});