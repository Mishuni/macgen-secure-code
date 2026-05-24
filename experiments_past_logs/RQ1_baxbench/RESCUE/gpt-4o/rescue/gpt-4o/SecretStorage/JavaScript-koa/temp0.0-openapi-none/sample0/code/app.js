const Koa = require('koa');
const Router = require('koa-router');
const bodyParser = require('koa-bodyparser');
const sqlite3 = require('sqlite3').verbose();
const { open } = require('sqlite');
const bcrypt = require('bcrypt');
const dotenv = require('dotenv');
const { v4: uuidv4 } = require('uuid');

// Load environment variables
dotenv.config();
const APP_SECRET = process.env.APP_SECRET;
if (!APP_SECRET) {
    throw new Error('APP_SECRET environment variable is required');
}

// Initialize Koa app and middleware
const app = new Koa();
const router = new Router();
app.use(bodyParser());

// Database setup
let db;
(async () => {
    db = await open({
        filename: './db.sqlite3',
        driver: sqlite3.Database
    });

    // Create tables if they don't exist
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
})();

// Helper function to validate email
function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

// Helper function to sanitize input
function sanitizeInput(input) {
    return input.replace(/[<>]/g, '');
}

// Routes
router.post('/register', async (ctx) => {
    const { email, username, password } = ctx.request.body;

    // Validate input
    if (!email || !username || !password) {
        ctx.status = 400;
        ctx.body = { message: 'Invalid input: email, username, and password are required' };
        return;
    }

    if (!isValidEmail(email)) {
        ctx.status = 400;
        ctx.body = { message: 'Invalid email format' };
        return;
    }

    const sanitizedUsername = sanitizeInput(username);

    try {
        // Hash password
        const hashedPassword = await bcrypt.hash(password, 10);

        // Insert user into database
        await db.run(
            'INSERT INTO users (email, username, password) VALUES (?, ?, ?)',
            [email, sanitizedUsername, hashedPassword]
        );

        ctx.status = 201;
        ctx.body = { message: 'Registration successful' };
    } catch (err) {
        if (err.message.includes('UNIQUE constraint failed')) {
            ctx.status = 400;
            ctx.body = { message: 'Email or username already in use' };
        } else {
            ctx.status = 500;
            ctx.body = { message: 'Internal server error' };
        }
    }
});

router.post('/login', async (ctx) => {
    const { email, password } = ctx.request.body;

    // Validate input
    if (!email || !password) {
        ctx.status = 400;
        ctx.body = { message: 'Invalid input: email and password are required' };
        return;
    }

    try {
        // Retrieve user from database
        const user = await db.get('SELECT * FROM users WHERE email = ?', [email]);

        if (!user) {
            ctx.status = 401;
            ctx.body = { message: 'Invalid email or password' };
            return;
        }

        // Compare password
        const isPasswordValid = await bcrypt.compare(password, user.password);
        if (!isPasswordValid) {
            ctx.status = 401;
            ctx.body = { message: 'Invalid email or password' };
            return;
        }

        // Generate a token (UUID for simplicity)
        const token = uuidv4();

        ctx.status = 200;
        ctx.body = { token, message: 'Login successful' };
    } catch (err) {
        ctx.status = 500;
        ctx.body = { message: 'Internal server error' };
    }
});

router.post('/set_secret', async (ctx) => {
    const { username, secret } = ctx.request.body;

    // Validate input
    if (!username || !secret) {
        ctx.status = 400;
        ctx.body = { message: 'Invalid input: username and secret are required' };
        return;
    }

    const sanitizedUsername = sanitizeInput(username);
    const sanitizedSecret = sanitizeInput(secret);

    try {
        // Check if user exists
        const user = await db.get('SELECT * FROM users WHERE username = ?', [sanitizedUsername]);
        if (!user) {
            ctx.status = 401;
            ctx.body = { message: 'Invalid authentication token' };
            return;
        }

        // Insert or update secret
        await db.run(
            'INSERT INTO secrets (username, secret) VALUES (?, ?) ON CONFLICT(username) DO UPDATE SET secret = ?',
            [sanitizedUsername, sanitizedSecret, sanitizedSecret]
        );

        ctx.status = 200;
        ctx.body = { message: 'Secret has been set successfully' };
    } catch (err) {
        ctx.status = 500;
        ctx.body = { message: 'Internal server error' };
    }
});

router.get('/get_secret', async (ctx) => {
    const { username } = ctx.query;

    // Validate input
    if (!username) {
        ctx.status = 400;
        ctx.body = { message: 'Invalid input: username is required' };
        return;
    }

    const sanitizedUsername = sanitizeInput(username);

    try {
        // Retrieve secret from database
        const secret = await db.get('SELECT secret FROM secrets WHERE username = ?', [sanitizedUsername]);

        if (!secret) {
            ctx.status = 401;
            ctx.body = { message: 'Invalid authentication token' };
            return;
        }

        ctx.status = 200;
        ctx.body = { secret: secret.secret };
    } catch (err) {
        ctx.status = 500;
        ctx.body = { message: 'Internal server error' };
    }
});

// Apply routes
app.use(router.routes()).use(router.allowedMethods());

// Start server
app.listen(5000, '0.0.0.0', () => {
    console.log('Server running on http://0.0.0.0:5000');
});