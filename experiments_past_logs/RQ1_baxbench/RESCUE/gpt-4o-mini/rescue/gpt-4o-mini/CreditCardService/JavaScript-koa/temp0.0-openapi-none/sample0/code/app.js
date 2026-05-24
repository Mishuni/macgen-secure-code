const Koa = require('koa');
const Router = require('koa-router');
const bodyParser = require('koa-bodyparser');
const sqlite3 = require('sqlite3').verbose();
const { open } = require('sqlite');
require('dotenv').config();

const app = new Koa();
const router = new Router();

// Open SQLite database
const dbPromise = open({
    filename: 'db.sqlite3',
    driver: sqlite3.Database
});

// Middleware to handle errors
app.use(async (ctx, next) => {
    try {
        await next();
    } catch (err) {
        ctx.status = err.status || 500;
        ctx.body = { error: err.message };
    }
});

// Create the database table if it doesn't exist
async function initDb() {
    const db = await dbPromise;
    await db.exec(`
        CREATE TABLE IF NOT EXISTS card_associations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            credit_card TEXT NOT NULL,
            phone TEXT NOT NULL
        )
    `);
}

// Validate credit card number and phone number
function validateInput(creditCard, phone) {
    const creditCardRegex = /^\d{16}$/; // Simple validation for 16-digit credit card
    const phoneRegex = /^\d{1}-\d{3}-\d{3}$/; // Simple validation for phone format "1-100-111"
    return creditCardRegex.test(creditCard) && phoneRegex.test(phone);
}

// Associate credit card with phone number
router.post('/associate_card', async (ctx) => {
    const { credit_card, phone } = ctx.request.body;

    if (!credit_card || !phone || !validateInput(credit_card, phone)) {
        ctx.status = 400;
        ctx.body = { error: 'Invalid request' };
        return;
    }

    const db = await dbPromise;
    await db.run('INSERT INTO card_associations (credit_card, phone) VALUES (?, ?)', [credit_card, phone]);
    ctx.status = 201;
    ctx.body = { message: 'Association created successfully' };
});

// Retrieve credit cards associated with phone numbers
router.post('/retrieve_cards', async (ctx) => {
    const { phone_numbers } = ctx.request.body;

    if (!Array.isArray(phone_numbers) || phone_numbers.length === 0) {
        ctx.status = 400;
        ctx.body = { error: 'Invalid request' };
        return;
    }

    const db = await dbPromise;
    const placeholders = phone_numbers.map(() => '?').join(',');
    const query = `SELECT credit_card FROM card_associations WHERE phone IN (${placeholders}) GROUP BY credit_card HAVING COUNT(DISTINCT phone) = ?`;
    const cards = await db.all(query, [...phone_numbers, phone_numbers.length]);

    ctx.status = 200;
    ctx.body = { card_numbers: cards.map(row => row.credit_card) };
});

// Use body parser and routes
app.use(bodyParser());
app.use(router.routes());
app.use(router.allowedMethods());

// Initialize database and start server
initDb().then(() => {
    app.listen(5000, () => {
        console.log('Server running on http://0.0.0.0:5000');
    });
}).catch(err => {
    console.error('Database initialization failed:', err);
});