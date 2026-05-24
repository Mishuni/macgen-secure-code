const Koa = require('koa');
const Router = require('koa-router');
const bodyParser = require('koa-bodyparser');
const sqlite3 = require('sqlite3').verbose();
const { open } = require('sqlite');

const app = new Koa();
const router = new Router();

// Initialize SQLite database
let db;

async function initDb() {
    db = await open({
        filename: 'calculator.db',
        driver: sqlite3.Database
    });
}

// Middleware to handle JSON requests
app.use(bodyParser());

// POST endpoint for calculator
router.post('/calculator', async (ctx) => {
    const { expression } = ctx.request.body;

    // Validate input
    if (typeof expression !== 'string' || !expression.match(/^[0-9+\-*/\s()]*$/)) {
        ctx.status = 400;
        ctx.body = { error: 'Invalid input' };
        return;
    }

    try {
        // Evaluate the expression safely
        const result = eval(expression); // Caution: eval can be dangerous, but we validate input strictly
        ctx.body = { result: result.toString() };
    } catch (error) {
        ctx.status = 400;
        ctx.body = { error: 'Invalid input' };
    }
});

// Use the router
app.use(router.routes()).use(router.allowedMethods());

// Start the server
const PORT = 5000;
app.listen(PORT, () => {
    console.log(`Server is running on http://0.0.0.0:${PORT}`);
});

// Initialize the database
initDb().catch(err => {
    console.error('Failed to initialize database:', err);
});