const Koa = require('koa');
const Router = require('koa-router');
const bodyParser = require('koa-bodyparser');
const sqlite3 = require('sqlite3').verbose();
const { open } = require('sqlite');
const { v4: uuidv4 } = require('uuid');
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
        CREATE TABLE IF NOT EXISTS invitations (
            id TEXT PRIMARY KEY,
            email TEXT UNIQUE NOT NULL
        );
    `);
    await db.exec(`
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            invite_id TEXT NOT NULL,
            FOREIGN KEY (invite_id) REFERENCES invitations (id)
        );
    `);
    return db;
};

// Middleware to handle errors
app.use(async (ctx, next) => {
    try {
        await next();
    } catch (err) {
        ctx.status = err.status || 500;
        ctx.body = { message: err.message };
    }
});

// Create an invitation
router.post('/invite_user', async (ctx) => {
    const { email } = ctx.request.body;
    const db = await initDb();

    const existingInvite = await db.get('SELECT id FROM invitations WHERE email = ?', email);
    if (existingInvite) {
        ctx.body = { invite_id: existingInvite.id, message: 'Invitation already exists.' };
        return;
    }

    const invite_id = uuidv4();
    await db.run('INSERT INTO invitations (id, email) VALUES (?, ?)', invite_id, email);
    ctx.body = { invite_id, message: 'Invitation email created.' };
});

// Create a user
router.post('/create_user', async (ctx) => {
    const { invite_id, user_name, password } = ctx.request.body;
    const db = await initDb();

    const invite = await db.get('SELECT email FROM invitations WHERE id = ?', invite_id);
    if (!invite) {
        ctx.status = 401;
        ctx.body = { message: 'Invalid invite_id' };
        return;
    }

    try {
        await db.run('INSERT INTO users (username, password, invite_id) VALUES (?, ?, ?)', user_name, password, invite_id);
        ctx.body = { message: 'User created' };
    } catch (err) {
        ctx.status = 400;
        ctx.body = { message: 'Username already exists. Try providing different username.' };
    }
});

// Use body parser and routes
app.use(bodyParser());
app.use(router.routes());
app.use(router.allowedMethods());

// Start the server
app.listen(5000, () => {
    console.log('Server running on http://0.0.0.0:5000');
});