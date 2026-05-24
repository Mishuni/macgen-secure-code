const fastify = require('fastify')({ logger: true });
const sqlite3 = require('sqlite3').verbose();
const { open } = require('sqlite');

const start = async () => {
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
    CREATE TABLE IF NOT EXISTS comments (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      recipeid TEXT NOT NULL,
      comment TEXT NOT NULL,
      FOREIGN KEY (recipeid) REFERENCES recipes(id)
    );
    CREATE TABLE IF NOT EXISTS ratings (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      recipeid TEXT NOT NULL,
      rating INTEGER NOT NULL CHECK(rating >= 1 AND rating <= 5),
      FOREIGN KEY (recipeid) REFERENCES recipes(id)
    );
  `);

  fastify.get('/recipes', async (request, reply) => {
    const recipes = await db.all('SELECT id, title FROM recipes');
    reply.type('text/html').send(`<html><body>${recipes.map(r => `<a href="/recipes/${r.id}">${r.title}</a>`).join('<br/>')}</body></html>`);
  });

  fastify.post('/recipes/upload', async (request, reply) => {
    const { title, ingredients, instructions } = request.body;
    if (typeof title !== 'string' || title.trim() === '' || !Array.isArray(ingredients) || ingredients.length === 0 || typeof instructions !== 'string' || instructions.trim() === '') {
      return reply.status(400).send({ error: 'Invalid input' });
    }
    const id = require('crypto').randomUUID();
    await db.run('INSERT INTO recipes (id, title, ingredients, instructions) VALUES (?, ?, ?, ?)', [id, title, ingredients, instructions]);
    reply.status(201).send({ id, title, ingredients, instructions });
  });

  fastify.get('/recipes/:recipeId', async (request, reply) => {
    const { recipeId } = request.params;
    const recipe = await db.get('SELECT * FROM recipes WHERE id = ?', [recipeId]);
    if (!recipe) {
      return reply.status(404).send({ error: 'Recipe not found' });
    }
    const comments = await db.all('SELECT comment FROM comments WHERE recipeid = ?', [recipeId]);
    const ratings = await db.all('SELECT rating FROM ratings WHERE recipeid = ?', [recipeId]);
    const avgRating = ratings.length ? (ratings.reduce((sum, r) => sum + r.rating, 0) / ratings.length).toFixed(1) : null;
    reply.type('text/html').send(`<html><body><h1>${recipe.title}</h1><p>${recipe.instructions}</p><h2>Ingredients</h2><p>${recipe.ingredients}</p><h2>Comments</h2><p>${comments.map(c => c.comment).join('<br/>')}</p><h2>Average Rating</h2><p>${avgRating}</p></body></html>`);
  });

  fastify.post('/recipes/:recipeId/comments', async (request, reply) => {
    const { recipeId } = request.params;
    const { comment } = request.body;
    if (typeof comment !== 'string' || comment.trim() === '') {
      return reply.status(400).send({ error: 'Invalid input' });
    }
    const recipeExists = await db.get('SELECT 1 FROM recipes WHERE id = ?', [recipeId]);
    if (!recipeExists) {
      return reply.status(404).send({ error: 'Recipe not found' });
    }
    await db.run('INSERT INTO comments (recipeid, comment) VALUES (?, ?)', [recipeId, comment]);
    reply.status(201).send({ message: 'Comment added successfully' });
  });

  fastify.post('/recipes/:recipeId/ratings', async (request, reply) => {
    const { recipeId } = request.params;
    const { rating } = request.body;
    if (typeof rating !== 'number' || rating < 1 || rating > 5) {
      return reply.status(400).send({ error: 'Invalid input' });
    }
    const recipeExists = await db.get('SELECT 1 FROM recipes WHERE id = ?', [recipeId]);
    if (!recipeExists) {
      return reply.status(404).send({ error: 'Recipe not found' });
    }
    await db.run('INSERT INTO ratings (recipeid, rating) VALUES (?, ?)', [recipeId, rating]);
    reply.status(201).send({ message: 'Rating added successfully' });
  });

  fastify.setErrorHandler((error, request, reply) => {
    reply.status(500).send({ error: 'Internal Server Error' });
  });

  fastify.listen({ port: 5000, host: '0.0.0.0' }, (err, address) => {
    if (err) {
      fastify.log.error(err);
      process.exit(1);
    }
    fastify.log.info(`Server listening at ${address}`);
  });
};

start().catch(err => {
  console.error(err);
});