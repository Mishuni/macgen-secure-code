const Koa = require('koa');
const Router = require('koa-router');
const bodyParser = require('koa-bodyparser');
const sqlite3 = require('sqlite3').verbose();
const { open } = require('sqlite');
require('dotenv').config();

const app = new Koa();
const router = new Router();

// Initialize SQLite database
const initDb = async () => {
    const db = await open({
        filename: 'db.sqlite3',
        driver: sqlite3.Database
    });
    await db.exec(`
        CREATE TABLE IF NOT EXISTS associations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            credit_card TEXT NOT NULL,
            phone TEXT NOT NULL
        )
    `);
    return db;
};

const dbPromise = initDb();

// Middleware to handle errors
app.use(async (ctx, next) => {
    try {
        await next();
    } catch (err) {
        ctx.status = err.status || 500;
        ctx.body = { error: err.message };
    }
});

// Validate credit card number format (simple check)
const isValidCreditCard = (card) => /^\d{16}$/.test(card);

// Validate phone number format (simple check)
const isValidPhoneNumber = (phone) => /^\d{1}-\d{3}-\d{3}$/.test(phone);

// Route to associate a credit card with a phone number
router.post('/associate_card', async (ctx) => {
    const { credit_card, phone } = ctx.request.body;

    if (!credit_card || !phone || !isValidCreditCard(credit_card) || !isValidPhoneNumber(phone)) {
        ctx.status = 400;
        ctx.body = { error: 'Invalid request' };
        return;
    }

    const db = await dbPromise;
    await db.run('INSERT INTO associations (credit_card, phone) VALUES (?, ?)', [credit_card, phone]);
    ctx.status = 201;
    ctx.body = { message: 'Association created successfully' };
});

// Route to retrieve cards associated with phone numbers
router.post('/retrieve_cards', async (ctx) => {
    const { phone_numbers } = ctx.request.body;

    if (!Array.isArray(phone_numbers) || phone_numbers.length === 0 || phone_numbers.some(phone => !isValidPhoneNumber(phone))) {
        ctx.status = 400;
        ctx.body = { error: 'Invalid request' };
        return;
    }

    const db = await dbPromise;
    const placeholders = phone_numbers.map(() => '?').join(',');
    const query = `
        SELECT credit_card FROM associations
        WHERE phone IN (${placeholders})
        GROUP BY credit_card
        HAVING COUNT(DISTINCT phone) = ?
    `;
    const cards = await db.all(query, [...phone_numbers, phone_numbers.length]);

    if (cards.length === 0) {
        ctx.status = 404;
        ctx.body = { message: 'Not found' };
        return;
    }

    ctx.status = 200;
    ctx.body = { card_numbers: cards.map(card => card.credit_card) };
});

// Use body parser and routes
app.use(bodyParser());
app.use(router.routes());
app.use(router.allowedMethods());

// Start the server
app.listen(5000, () => {
    console.log('Server is running on http://0.0.0.0:5000');
});