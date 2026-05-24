import Koa from 'koa';
import Router from 'koa-router';
import bodyParser from 'koa-bodyparser';
import sqlite3 from 'sqlite3';
import { open } from 'sqlite';
import dotenv from 'dotenv';

dotenv.config();

const app = new Koa();
const router = new Router();
const dbPromise = open({
    filename: 'db.sqlite3',
    driver: sqlite3.Database
});

// Initialize the database and create the table if it doesn't exist
async function initDatabase() {
    const db = await dbPromise;
    await db.exec(`
        CREATE TABLE IF NOT EXISTS card_associations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            credit_card TEXT NOT NULL,
            phone TEXT NOT NULL
        )
    `);
}

// Middleware for error handling
app.use(async (ctx, next) => {
    try {
        await next();
    } catch (err) {
        ctx.status = err.status || 500;
        ctx.body = { message: err.message };
    }
});

// Associate a credit card with a phone number
router.post('/associate_card', async (ctx) => {
    const { credit_card, phone } = ctx.request.body;

    if (typeof credit_card !== 'string' || typeof phone !== 'string') {
        ctx.status = 400;
        ctx.body = { message: 'Invalid request' };
        return;
    }

    const db = await dbPromise;
    await db.run('INSERT INTO card_associations (credit_card, phone) VALUES (?, ?)', [credit_card, phone]);
    ctx.status = 201;
});

// Retrieve credit cards associated with given phone numbers
router.post('/retrieve_cards', async (ctx) => {
    const { phone_numbers } = ctx.request.body;

    if (!Array.isArray(phone_numbers) || phone_numbers.length === 0) {
        ctx.status = 400;
        ctx.body = { message: 'Invalid request' };
        return;
    }

    const db = await dbPromise;
    const placeholders = phone_numbers.map(() => '?').join(',');
    const query = `
        SELECT credit_card FROM card_associations
        WHERE phone IN (${placeholders})
        GROUP BY credit_card
        HAVING COUNT(DISTINCT phone) = ?
    `;
    const cardNumbers = await db.all(query, [...phone_numbers, phone_numbers.length]);

    if (cardNumbers.length === 0) {
        ctx.status = 404;
        ctx.body = { message: 'Not found' };
        return;
    }

    ctx.status = 200;
    ctx.body = { card_numbers: cardNumbers.map(row => row.credit_card) };
});

// Use bodyParser and routes
app.use(bodyParser());
app.use(router.routes());
app.use(router.allowedMethods());

// Start the server and initialize the database
const startServer = async () => {
    await initDatabase();
    app.listen(5000, '0.0.0.0', () => {
        console.log('Server is running on http://0.0.0.0:5000');
    });
};

startServer();