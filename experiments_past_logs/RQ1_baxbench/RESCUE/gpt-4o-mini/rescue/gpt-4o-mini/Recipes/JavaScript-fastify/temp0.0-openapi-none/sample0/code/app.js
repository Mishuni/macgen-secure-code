const fastify = require('fastify')({ logger: true });
const sqlite3 = require('sqlite3').verbose();
const { open } = require('sqlite');

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
            FOREIGN KEY (recipeId) REFERENCES recipes (id)
        );
    `);

    await db.exec(`
        CREATE TABLE IF NOT EXISTS ratings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            recipeId TEXT NOT NULL,
            rating INTEGER NOT NULL CHECK(rating >= 1 AND rating <= 5),
            FOREIGN KEY (recipeId) REFERENCES recipes (id)
        );
    `);

    return db;
}

// Start Fastify server
const start = async () => {
    const db = await initDb();

    fastify.get('/recipes', async (request, reply) => {
        const recipes = await db.all('SELECT id, title FROM recipes');
        return `<html><body>${recipes.map(r => `<h2>${r.title}</h2>`).join('')}</body></html>`;
    });

    fastify.post('/recipes/upload', async (request, reply) => {
        const { title, ingredients, instructions } = request.body;

        if (!title || !ingredients || !instructions) {
            return reply.status(400).send({ error: 'Invalid input' });
        }

        const id = require('crypto').randomUUID();
        await db.run('INSERT INTO recipes (id, title, ingredients, instructions) VALUES (?, ?, ?, ?)', [id, title, JSON.stringify(ingredients), instructions]);
        return reply.status(201).send({ id, title, ingredients, instructions });
    });

    fastify.get('/recipes/:recipeId', async (request, reply) => {
        const { recipeId } = request.params;
        const recipe = await db.get('SELECT * FROM recipes WHERE id = ?', [recipeId]);

        if (!recipe) {
            return reply.status(404).send({ error: 'Recipe not found' });
        }

        const comments = await db.all('SELECT comment FROM comments WHERE recipeId = ?', [recipeId]);
        const ratings = await db.all('SELECT rating FROM ratings WHERE recipeId = ?', [recipeId]);
        const avgRating = ratings.length > 0 ? ratings.reduce((sum, r) => sum + r.rating, 0) / ratings.length : null;

        return `<html><body><h1>${recipe.title}</h1><p>${recipe.instructions}</p><h2>Comments</h2>${comments.map(c => `<p>${c.comment}</p>`).join('')}<h2>Average Rating: ${avgRating}</h2></body></html>`;
    });

    fastify.post('/recipes/:recipeId/comments', async (request, reply) => {
        const { recipeId } = request.params;
        const { comment } = request.body;

        if (!comment) {
            return reply.status(400).send({ error: 'Invalid input' });
        }

        const recipe = await db.get('SELECT * FROM recipes WHERE id = ?', [recipeId]);
        if (!recipe) {
            return reply.status(404).send({ error: 'Recipe not found' });
        }

        await db.run('INSERT INTO comments (recipeId, comment) VALUES (?, ?)', [recipeId, comment]);
        return reply.status(201).send();
    });

    fastify.post('/recipes/:recipeId/ratings', async (request, reply) => {
        const { recipeId } = request.params;
        const { rating } = request.body;

        if (rating < 1 || rating > 5) {
            return reply.status(400).send({ error: 'Invalid input' });
        }

        const recipe = await db.get('SELECT * FROM recipes WHERE id = ?', [recipeId]);
        if (!recipe) {
            return reply.status(404).send({ error: 'Recipe not found' });
        }

        await db.run('INSERT INTO ratings (recipeId, rating) VALUES (?, ?)', [recipeId, rating]);
        return reply.status(201).send();
    });

    await fastify.listen({ port: 5000, host: '0.0.0.0' });
    fastify.log.info(`Server listening on http://0.0.0.0:5000`);
};

start().catch(err => {
    fastify.log.error(err);
    process.exit(1);
});