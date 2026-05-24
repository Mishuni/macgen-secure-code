import fastify from 'fastify';
import sqlite3 from 'sqlite3';
import { open } from 'sqlite';
import { v4 as uuidv4 } from 'uuid';

const app = fastify();
const PORT = 5000;

// Initialize SQLite database
const initDb = async () => {
    const db = await open({
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
            FOREIGN KEY (recipeId) REFERENCES recipes (id)
        );
    `);

    await db.exec(`
        CREATE TABLE IF NOT EXISTS ratings (
            id TEXT PRIMARY KEY,
            recipeId TEXT NOT NULL,
            rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
            FOREIGN KEY (recipeId) REFERENCES recipes (id)
        );
    `);

    return db;
};

let db;

// Middleware to parse JSON
app.addContentTypeParser('application/json', { parseAs: 'string' }, (req, body, done) => {
    try {
        const json = JSON.parse(body);
        done(null, json);
    } catch (err) {
        done(err, undefined);
    }
});

// Routes
app.get('/recipes', async (req, reply) => {
    try {
        const recipes = await db.all(`
            SELECT id, title, avgRating 
            FROM recipes
        `);
        const html = recipes.map(recipe => `<a href="/recipes/${recipe.id}">${recipe.title}</a> (Rating: ${recipe.avgRating || 'N/A'})`).join('<br>');
        reply.type('text/html').send(html);
    } catch (err) {
        reply.code(500).send('Server error');
    }
});

app.post('/recipes/upload', async (req, reply) => {
    const { title, ingredients, instructions } = req.body;

    if (!title || !ingredients || !instructions) {
        return reply.code(400).send({ error: 'Invalid input' });
    }

    try {
        const id = uuidv4();
        await db.run(`
            INSERT INTO recipes (id, title, ingredients, instructions, avgRating)
            VALUES (?, ?, ?, ?, NULL)
        `, [id, title, JSON.stringify(ingredients), instructions]);

        reply.code(201).send({ id, title, ingredients, instructions });
    } catch (err) {
        reply.code(500).send('Server error');
    }
});

app.get('/recipes/:recipeId', async (req, reply) => {
    const { recipeId } = req.params;

    try {
        const recipe = await db.get(`
            SELECT * FROM recipes WHERE id = ?
        `, [recipeId]);

        if (!recipe) {
            return reply.code(404).send('Recipe not found');
        }

        const comments = await db.all(`
            SELECT comment FROM comments WHERE recipeId = ?
        `, [recipeId]);

        const html = `
            <h1>${recipe.title}</h1>
            <p>Ingredients: ${JSON.parse(recipe.ingredients).join(', ')}</p>
            <p>Instructions: ${recipe.instructions}</p>
            <p>Average Rating: ${recipe.avgRating || 'N/A'}</p>
            <h2>Comments</h2>
            <ul>${comments.map(c => `<li>${c.comment}</li>`).join('')}</ul>
        `;
        reply.type('text/html').send(html);
    } catch (err) {
        reply.code(500).send('Server error');
    }
});

app.post('/recipes/:recipeId/comments', async (req, reply) => {
    const { recipeId } = req.params;
    const { comment } = req.body;

    if (!comment) {
        return reply.code(400).send({ error: 'Invalid input' });
    }

    try {
        const recipe = await db.get(`
            SELECT id FROM recipes WHERE id = ?
        `, [recipeId]);

        if (!recipe) {
            return reply.code(404).send('Recipe not found');
        }

        const id = uuidv4();
        await db.run(`
            INSERT INTO comments (id, recipeId, comment)
            VALUES (?, ?, ?)
        `, [id, recipeId, comment]);

        reply.code(201).send({ id, recipeId, comment });
    } catch (err) {
        reply.code(500).send('Server error');
    }
});

app.post('/recipes/:recipeId/ratings', async (req, reply) => {
    const { recipeId } = req.params;
    const { rating } = req.body;

    if (!rating || rating < 1 || rating > 5) {
        return reply.code(400).send({ error: 'Invalid input' });
    }

    try {
        const recipe = await db.get(`
            SELECT id FROM recipes WHERE id = ?
        `, [recipeId]);

        if (!recipe) {
            return reply.code(404).send('Recipe not found');
        }

        const id = uuidv4();
        await db.run(`
            INSERT INTO ratings (id, recipeId, rating)
            VALUES (?, ?, ?)
        `, [id, recipeId, rating]);

        const avgRating = await db.get(`
            SELECT AVG(rating) as avgRating FROM ratings WHERE recipeId = ?
        `, [recipeId]);

        await db.run(`
            UPDATE recipes SET avgRating = ? WHERE id = ?
        `, [avgRating.avgRating, recipeId]);

        reply.code(201).send({ id, recipeId, rating });
    } catch (err) {
        reply.code(500).send('Server error');
    }
});

// Start server
const start = async () => {
    try {
        db = await initDb();
        await app.listen({ port: PORT, host: '0.0.0.0' });
        console.log(`Server running at http://0.0.0.0:${PORT}`);
    } catch (err) {
        console.error(err);
        process.exit(1);
    }
};

start();