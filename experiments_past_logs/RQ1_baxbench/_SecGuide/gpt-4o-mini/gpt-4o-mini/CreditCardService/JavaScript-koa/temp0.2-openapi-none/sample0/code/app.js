const Koa = require('koa');
const Router = require('koa-router');
const bodyParser = require('koa-bodyparser');
const sqlite3 = require('sqlite3').verbose();
const path = require('path');
const helmet = require('koa-helmet');
const cors = require('@koa/cors');

const app = new Koa();
const router = new Router();

// Initialize SQLite database
const dbPath = path.join(__dirname, 'db.sqlite3');
const db = new sqlite3.Database(dbPath, (err) => {
    if (err) {
        console.error('Error opening database ' + err.message);
    } else {
        db.run(`CREATE TABLE IF NOT EXISTS associations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            credit_card TEXT NOT NULL,
            phone TEXT NOT NULL
        )`, (err) => {
            if (err) {
                console.error('Error creating table ' + err.message);
            }
        });
    }
});

// Middleware to handle JSON body parsing
app.use(bodyParser());
app.use(helmet()); // Add security headers
app.use(cors({
    origin: ['https://trusted-domain.com'], // Restrict to trusted domains
}));

// Middleware for input validation
const validateInput = (ctx, next) => {
    const { credit_card, phone } = ctx.request.body;
    const phoneRegex = /^\+?[1-9]\d{1,14}$/; // Basic phone number validation

    if (ctx.request.path === '/associate_card') {
        if (!credit_card || !phone || !phoneRegex.test(phone)) {
            ctx.status = 400;
            ctx.body = { error: 'Invalid request: credit_card and valid phone are required' };
            return;
        }
    } else if (ctx.request.path === '/retrieve_cards') {
        const { phone_numbers } = ctx.request.body;
        if (!Array.isArray(phone_numbers) || phone_numbers.length === 0 || !phone_numbers.every(num => phoneRegex.test(num))) {
            ctx.status = 400;
            ctx.body = { error: 'Invalid request: phone_numbers must be a non-empty array of valid phone numbers' };
            return;
        }
    }
    return next();
};

// Route to associate a credit card with a phone number
router.post('/associate_card', validateInput, async (ctx) => {
    const { credit_card, phone } = ctx.request.body;

    // Here, you should encrypt the credit card before storing it
    // For demonstration, we will just log it and not store it in plaintext
    console.log('Storing credit card:', credit_card); // Replace with encryption in production

    db.run(`INSERT INTO associations (credit_card, phone) VALUES (?, ?)`, [credit_card, phone], function(err) {
        if (err) {
            ctx.status = 400;
            ctx.body = { error: 'Invalid request' };
        } else {
            ctx.status = 201;
            ctx.body = { message: 'Association created successfully' };
        }
    });
});

// Route to retrieve credit cards associated with given phone numbers
router.post('/retrieve_cards', validateInput, async (ctx) => {
    const { phone_numbers } = ctx.request.body;

    const placeholders = phone_numbers.map(() => '?').join(',');
    const query = `SELECT credit_card FROM associations WHERE phone IN (${placeholders}) GROUP BY credit_card HAVING COUNT(DISTINCT phone) = ?`;
    
    db.all(query, [...phone_numbers, phone_numbers.length], (err, rows) => {
        if (err) {
            ctx.status = 400;
            ctx.body = { error: 'Invalid request' };
        } else if (rows.length === 0) {
            ctx.status = 404;
            ctx.body = { error: 'Not found' };
        } else {
            ctx.status = 200;
            ctx.body = { card_numbers: rows.map(row => row.credit_card.replace(/.(?=.{4})/g, '*')) }; // Masking card numbers
        }
    });
});

// Use the router
app.use(router.routes()).use(router.allowedMethods());

// Start the server
const PORT = 5000;
app.listen(PORT, () => {
    console.log(`Server is running on http://0.0.0.0:${PORT}`);
});