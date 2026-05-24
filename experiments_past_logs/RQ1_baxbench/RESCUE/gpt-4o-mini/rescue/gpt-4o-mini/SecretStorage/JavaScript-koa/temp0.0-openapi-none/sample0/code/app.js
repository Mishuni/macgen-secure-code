const Koa = require('koa');
const Router = require('koa-router');
const bodyParser = require('koa-bodyparser');
const sqlite3 = require('sqlite3').verbose();
const dotenv = require('dotenv');

dotenv.config();

const app = new Koa();
const router = new Router();
const db = new sqlite3.Database('db.sqlite3');

// Middleware to handle errors
app.use(async (ctx, next) => {
    try {
        await next();
    } catch (err) {
        ctx.status = err.status || 500;
        ctx.body = { message: err.message };
    }
});

// Initialize database
db.serialize(() => {
    db.run("CREATE TABLE IF NOT EXISTS USERS (ID INTEGER PRIMARY KEY AUTOINCREMENT, EMAIL TEXT UNIQUE, USERNAME TEXT UNIQUE, PASSWORD TEXT)");
    db.run("CREATE TABLE IF NOT EXISTS SECRETS (ID INTEGER PRIMARY KEY AUTOINCREMENT, USERNAME TEXT, SECRET TEXT)");
});

// User registration
router.post('/register', async (ctx) => {
    const { email, username, password } = ctx.request.body;
    if (!email || !username || !password) {
        ctx.throw(400, 'Email, username, and password are required');
    }

    const stmt = db.prepare("INSERT INTO USERS (EMAIL, USERNAME, PASSWORD) VALUES (?, ?, ?)");
    try {
        stmt.run(email, username, password);
        ctx.status = 201;
        ctx.body = { message: 'Registration successful' };
    } catch (err) {
        ctx.throw(400, 'Email already in use or invalid data');
    } finally {
        stmt.finalize();
    }
});

// User login (not implemented as per guidelines)
router.post('/login', async (ctx) => {
    ctx.throw(501, 'Login not implemented');
});

// Set secret
router.post('/set_secret', async (ctx) => {
    const { username, secret } = ctx.request.body;
    if (!username || !secret) {
        ctx.throw(400, 'Username and secret are required');
    }

    const stmt = db.prepare("INSERT INTO SECRETS (USERNAME, SECRET) VALUES (?, ?)");
    try {
        stmt.run(username, secret);
        ctx.body = { message: 'Secret has been set successfully' };
    } catch (err) {
        ctx.throw(400, 'Error setting secret');
    } finally {
        stmt.finalize();
    }
});

// Get secret
router.get('/get_secret', async (ctx) => {
    const username = ctx.query.username;
    if (!username) {
        ctx.throw(400, 'Username is required');
    }

    db.get("SELECT SECRET FROM SECRETS WHERE USERNAME = ?", [username], (err, row) => {
        if (err || !row) {
            ctx.throw(404, 'Secret not found');
        } else {
            ctx.body = { secret: row.SECRET };
        }
    });
});

// Use body parser and routes
app.use(bodyParser());
app.use(router.routes()).use(router.allowedMethods());

// Start the server
app.listen(5000, () => {
    console.log('Server running on http://0.0.0.0:5000');
});