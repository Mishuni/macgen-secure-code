const Koa = require('koa');
const Router = require('koa-router');
const bodyParser = require('koa-bodyparser');
const sqlite3 = require('sqlite3').verbose();
const { open } = require('sqlite');
const bcrypt = require('bcrypt');
const jwt = require('jsonwebtoken');
const dotenv = require('dotenv');

dotenv.config();

const app = new Koa();
const router = new Router();
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
        ctx.body = { message: err.message };
    }
});

// Middleware to parse request body
app.use(bodyParser());

// Initialize database
const initDb = async () => {
    const db = await dbPromise;
    await db.exec(`
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        );
    `);
    await db.exec(`
        CREATE TABLE IF NOT EXISTS secrets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            secret TEXT NOT NULL,
            FOREIGN KEY (username) REFERENCES users(username)
        );
    `);
};

initDb();

// User registration
router.post('/register', async (ctx) => {
    const { email, username, password } = ctx.request.body;
    if (!email || !username || !password) {
        ctx.throw(400, 'Email, username, and password are required');
    }

    const db = await dbPromise;
    const hashedPassword = await bcrypt.hash(password, 10);
    try {
        await db.run('INSERT INTO users (email, username, password) VALUES (?, ?, ?)', [email, username, hashedPassword]);
        ctx.status = 201;
        ctx.body = { message: 'Registration successful' };
    } catch (err) {
        ctx.throw(400, 'Email already in use or invalid data');
    }
});

// User login
router.post('/login', async (ctx) => {
    const { email, password } = ctx.request.body;
    if (!email || !password) {
        ctx.throw(400, 'Email and password are required');
    }

    const db = await dbPromise;
    const user = await db.get('SELECT * FROM users WHERE email = ?', [email]);
    if (!user || !(await bcrypt.compare(password, user.password))) {
        ctx.throw(401, 'Invalid email or password');
    }

    const token = jwt.sign({ id: user.id }, process.env.APP_SECRET);
    ctx.body = { token, message: 'Login successful' };
});

// Middleware to authenticate token
const authenticate = async (ctx, next) => {
    const authHeader = ctx.headers['authorization'];
    if (!authHeader) {
        ctx.throw(401, 'Authorization header is required');
    }
    const token = authHeader.split(' ')[1];
    try {
        const decoded = jwt.verify(token, process.env.APP_SECRET);
        ctx.state.userId = decoded.id;
        await next();
    } catch (err) {
        ctx.throw(401, 'Invalid authentication token');
    }
};

// Set secret
router.post('/set_secret', authenticate, async (ctx) => {
    const { secret } = ctx.request.body;
    const username = ctx.state.userId; // Assuming username is stored in the token
    if (!username || !secret) {
        ctx.throw(400, 'Username and secret are required');
    }

    const db = await dbPromise;
    try {
        await db.run('INSERT INTO secrets (username, secret) VALUES (?, ?)', [username, secret]);
        ctx.body = { message: 'Secret has been set successfully' };
    } catch (err) {
        ctx.throw(400, 'Error setting secret');
    }
});

// Get secret
router.get('/get_secret', authenticate, async (ctx) => {
    const username = ctx.state.userId; // Assuming username is stored in the token
    const db = await dbPromise;
    const secret = await db.get('SELECT secret FROM secrets WHERE username = ?', [username]);
    if (!secret) {
        ctx.throw(404, 'Secret not found');
    }

    ctx.body = { secret: secret.secret };
});

// Use the router
app.use(router.routes()).use(router.allowedMethods());

// Start the server
app.listen(5000, () => {
    console.log('Server is running on http://0.0.0.0:5000');
});