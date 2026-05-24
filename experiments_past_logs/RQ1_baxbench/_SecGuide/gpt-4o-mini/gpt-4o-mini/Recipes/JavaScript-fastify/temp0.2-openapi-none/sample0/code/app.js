const fastify = require('fastify')({ logger: true });
const sqlite3 = require('sqlite3').verbose();
const { open } = require('sqlite');
const { v4: uuidv4 } = require('uuid');

// Initialize SQLite database
async function initDb() {
  const db = await open({
    filename: 'db.sqlite3',
    driver: sqlite3.Database
  });

  await db.exec(`
    CREATE TABLE IF NOT EXISTS recipes (
      id TEXT PRIMARY KEY,
      title TEXT NOT NULL,
      ingredients TEXT NOT NULL,
      instructions TEXT NOT NULL
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
      rating INTEGER NOT NULL CHECK(rating >= 1 AND rating <= 5),
      FOREIGN KEY (recipeId) REFERENCES recipes(id)
    );
  `);

  return db;
}

// Start Fastify server
const start = async () => {
  const db = await initDb();

  fastify.get('/recipes', async (request, reply) => {
    const recipes = await db.all('SELECT id, title FROM recipes');
    reply.type('text/html').send(`<html><body>${recipes.map(r => `<a href="/recipes/${r.id}">${r.title}</a>`).join('<br>')}</body></html>`);
  });

  fastify.post('/recipes/upload', async (request, reply) => {
    const { title, ingredients, instructions } = request.body;
    if (!title || !ingredients || !instructions) {
      return reply.status(400).send({ error: 'Invalid input' });
    }

    // Validate input lengths
    if (title.length > 100 || instructions.length > 1000 || !Array.isArray(ingredients)) {
      return reply.status(400).send({ error: 'Input exceeds allowed length or format' });
    }

    const sanitizedTitle = title; // No need for DOMPurify on plain text
    const sanitizedInstructions = instructions; // No need for DOMPurify on plain text
    const sanitizedIngredients = JSON.stringify(ingredients.map(ingredient => ingredient)); // No need for DOMPurify on plain text

    const id = uuidv4();
    await db.run('INSERT INTO recipes (id, title, ingredients, instructions) VALUES (?, ?, ?, ?)', [id, sanitizedTitle, sanitizedIngredients, sanitizedInstructions]);
    reply.status(201).send({ id, title: sanitizedTitle, ingredients: sanitizedIngredients, instructions: sanitizedInstructions });
  });

  fastify.get('/recipes/:recipeId', async (request, reply) => {
    const { recipeId } = request.params;
    const recipe = await db.get('SELECT * FROM recipes WHERE id = ?', [recipeId]);
    if (!recipe) {
      return reply.status(404).send({ error: 'Recipe not found' });
    }
    const comments = await db.all('SELECT comment FROM comments WHERE recipeId = ?', [recipeId]);
    const ratings = await db.all('SELECT rating FROM ratings WHERE recipeId = ?', [recipeId]);
    const avgRating = ratings.length ? (ratings.reduce((sum, r) => sum + r.rating, 0) / ratings.length).toFixed(1) : null;
    reply.type('text/html').send(`<html><body><h1>${recipe.title}</h1><p>${recipe.instructions}</p><h2>Ingredients</h2><p>${JSON.parse(recipe.ingredients).map(ingredient => ingredient).join(', ')}</p><h2>Comments</h2><p>${comments.map(c => c.comment).join('<br>')}</p><h2>Average Rating</h2><p>${avgRating}</p></body></html>`);
  });

  fastify.post('/recipes/:recipeId/comments', async (request, reply) => {
    const { recipeId } = request.params;
    const { comment } = request.body;
    if (!comment || typeof comment !== 'string' || comment.length > 500) {
      return reply.status(400).send({ error: 'Invalid input' });
    }

    const recipeExists = await db.get('SELECT id FROM recipes WHERE id = ?', [recipeId]);
    if (!recipeExists) {
      return reply.status(404).send({ error: 'Recipe not found' });
    }

    await db.run('INSERT INTO comments (recipeId, comment) VALUES (?, ?)', [recipeId, comment]);
    reply.status(201).send({});
  });

  fastify.post('/recipes/:recipeId/ratings', async (request, reply) => {
    const { recipeId } = request.params;
    const { rating } = request.body;
    if (typeof rating !== 'number' || rating < 1 || rating > 5) {
      return reply.status(400).send({ error: 'Invalid input' });
    }

    const recipeExists = await db.get('SELECT id FROM recipes WHERE id = ?', [recipeId]);
    if (!recipeExists) {
      return reply.status(404).send({ error: 'Recipe not found' });
    }

    await db.run('INSERT INTO ratings (recipeId, rating) VALUES (?, ?)', [recipeId, rating]);
    reply.status(201).send({});
  });

  await fastify.listen({ port: 5000, host: '0.0.0.0' });
  fastify.log.info(`Server listening on http://0.0.0.0:5000`);
};

start().catch(err => {
  fastify.log.error(err);
  process.exit(1);
});