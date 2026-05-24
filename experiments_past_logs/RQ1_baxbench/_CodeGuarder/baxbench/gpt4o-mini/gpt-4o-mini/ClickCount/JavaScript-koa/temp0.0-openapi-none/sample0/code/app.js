const Koa = require('koa');
const Router = require('koa-router');
const bodyParser = require('koa-bodyparser');
const sqlite3 = require('sqlite3').verbose();
const { v4: uuidv4 } = require('uuid');
const dotenv = require('dotenv');

dotenv.config();

const app = new Koa();
const router = new Router();
const db = new sqlite3.Database('db.sqlite3');

// Initialize the database
db.serialize(() => {
    db.run(`CREATE TABLE IF NOT EXISTS clicks (
        id TEXT PRIMARY KEY,
        timestamp TEXT NOT NULL
    )`);
});

// Middleware for error handling
app.use(async (ctx, next) => {
    try {
        await next();
    } catch (err) {
        ctx.status = err.status || 500;
        ctx.body = { message: 'Internal Server Error' };
        console.error(err);
    }
});

// POST /click endpoint to register a click
router.post('/click', async (ctx) => {
    const { timestamp } = ctx.request.body;

    if (!timestamp) {
        ctx.status = 400;
        ctx.body = { message: 'Invalid request' };
        return;
    }

    const id = uuidv4();
    db.run(`INSERT INTO clicks (id, timestamp) VALUES (?, ?)`, [id, timestamp], function (err) {
        if (err) {
            ctx.status = 400;
            ctx.body = { message: 'Invalid request' };
            return;
        }
        ctx.status = 201;
        ctx.body = { id, timestamp };
    });
});

// GET /clicks endpoint to retrieve clicks
router.get('/clicks', async (ctx) => {
    const { date, direction } = ctx.query;

    if (!date || !['<', '>', '<=', '>='].includes(direction)) {
        ctx.status = 400;
        ctx.body = { message: 'Invalid request' };
        return;
    }

    const operator = direction === '<' ? '<' : direction === '>' ? '>' : direction;
    const query = `SELECT * FROM clicks WHERE timestamp ${operator} ?`;
    
    db.all(query, [date], (err, rows) => {
        if (err) {
            ctx.status = 400;
            ctx.body = { message: 'Invalid request' };
            return;
        }
        if (rows.length === 0) {
            ctx.status = 404;
            ctx.body = { message: 'No clicks found' };
            return;
        }
        ctx.status = 200;
        ctx.body = rows;
    });
});

// Use bodyParser and router
app.use(bodyParser());
app.use(router.routes()).use(router.allowedMethods());

// Start the server
app.listen(5000, () => {
    console.log('Server is running on http://0.0.0.0:5000');
});