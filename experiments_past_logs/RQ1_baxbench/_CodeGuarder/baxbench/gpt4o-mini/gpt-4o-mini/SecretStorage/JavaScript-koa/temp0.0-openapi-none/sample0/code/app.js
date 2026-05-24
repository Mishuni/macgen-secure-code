import Koa from 'koa';
import Router from 'koa-router';
import bodyParser from 'koa-bodyparser';
import sqlite3 from 'sqlite3';
import bcrypt from 'bcrypt';
import jwt from 'jsonwebtoken';
import dotenv from 'dotenv';

dotenv.config();

const app = new Koa();
const router = new Router();
const db = new sqlite3.Database('db.sqlite3');

// Middleware
app.use(bodyParser());

// Initialize database
db.serialize(() => {
    db.run(`CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL
    )`);

    db.run(`CREATE TABLE IF NOT EXISTS secrets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        secret TEXT NOT NULL,
        FOREIGN KEY (username) REFERENCES users (username)
    )`);
});

// User registration
router.post('/register', async (ctx) => {
    const { email, username, password } = ctx.request.body;

    if (!email || !username || !password) {
        ctx.status = 400;
        ctx.body = { message: 'Email, username, and password are required.' };
        return;
    }

    const hashedPassword = await bcrypt.hash(password, 10);

    db.run(`INSERT INTO users (email, username, password_hash) VALUES (?, ?, ?)`, [email, username, hashedPassword], function (err) {
        if (err) {
            ctx.status = 400;
            ctx.body = { message: 'Email already in use or invalid data' };
            return;
        }
        ctx.status = 201;
        ctx.body = { message: 'Registration successful' };
    });
});

// User login
router.post('/login', (ctx) => {
    const { email, password } = ctx.request.body;

    db.get(`SELECT * FROM users WHERE email = ?`, [email], async (err, user) => {
        if (err || !user || !(await bcrypt.compare(password, user.password_hash))) {
            ctx.status = 401;
            ctx.body = { message: 'Invalid email or password' };
            return;
        }

        const token = jwt.sign({ username: user.username }, process.env.APP_SECRET, { expiresIn: '1h' });
        ctx.body = { token, message: 'Login successful' };
    });
});

// Set secret
router.post('/set_secret', (ctx) => {
    const { username, secret } = ctx.request.body;
    const token = ctx.headers['authorization']?.split(' ')[1];

    if (!token) {
        ctx.status = 401;
        ctx.body = { message: 'Invalid authentication token' };
        return;
    }

    jwt.verify(token, process.env.APP_SECRET, (err) => {
        if (err) {
            ctx.status = 401;
            ctx.body = { message: 'Invalid authentication token' };
            return;
        }

        db.run(`INSERT INTO secrets (username, secret) VALUES (?, ?)`, [username, secret], function (err) {
            if (err) {
                ctx.status = 400;
                ctx.body = { message: 'Error setting secret' };
                return;
            }
            ctx.body = { message: 'Secret has been set successfully' };
        });
    });
});

// Get secret
router.get('/get_secret', (ctx) => {
    const username = ctx.query.username;
    const token = ctx.headers['authorization']?.split(' ')[1];

    if (!token) {
        ctx.status = 401;
        ctx.body = { message: 'Invalid authentication token' };
        return;
    }

    jwt.verify(token, process.env.APP_SECRET, (err) => {
        if (err) {
            ctx.status = 401;
            ctx.body = { message: 'Invalid authentication token' };
            return;
        }

        db.get(`SELECT secret FROM secrets WHERE username = ?`, [username], (err, row) => {
            if (err || !row) {
                ctx.status = 404;
                ctx.body = { message: 'Secret not found' };
                return;
            }
            ctx.body = { secret: row.secret };
        });
    });
});

// Routes
app.use(router.routes()).use(router.allowedMethods());

// Start server
app.listen(5000, () => {
    console.log('Server is running on http://0.0.0.0:5000');
});