const Koa = require('koa');
const Router = require('koa-router');
const bodyParser = require('koa-bodyparser');
const sqlite3 = require('sqlite3').verbose();
const { open } = require('sqlite');
const { v4: uuidv4 } = require('uuid');
require('dotenv').config();

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
        ctx.app.emit('error', err, ctx);
    }
});

// Middleware for body parsing
app.use(bodyParser());

// Initialize database and create tables
async function initDb() {
    const db = await dbPromise;
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
}

// Endpoint to invite a user
router.post('/invite_user', async (ctx) => {
    const { email } = ctx.request.body;

    if (!email || !/^[\w-]+(\.[\w-]+)*@([\w-]+\.)+[a-zA-Z]{2,7}$/.test(email)) {
        ctx.throw(400, 'Invalid email format');
    }

    const db = await dbPromise;
    let inviteId;

    const existingInvite = await db.get('SELECT id FROM invitations WHERE email = ?', email);
    if (existingInvite) {
        inviteId = existingInvite.id;
    } else {
        inviteId = uuidv4();
        await db.run('INSERT INTO invitations (id, email) VALUES (?, ?)', inviteId, email);
    }

    ctx.body = {
        invite_id: inviteId,
        message: 'Invitation processed successfully'
    };
});

// Endpoint to create a user
router.post('/create_user', async (ctx) => {
    const { invite_id, user_name, password } = ctx.request.body;

    if (!invite_id || !user_name || !password) {
        ctx.throw(400, 'All fields are required');
    }

    const db = await dbPromise;
    const invite = await db.get('SELECT id FROM invitations WHERE id = ?', invite_id);

    if (!invite) {
        ctx.throw(401, 'Invalid invite_id');
    }

    const existingUser = await db.get('SELECT id FROM users WHERE username = ?', user_name);
    if (existingUser) {
        ctx.throw(400, 'Username already exists. Try providing a different username.');
    }

    await db.run('INSERT INTO users (username, password, invite_id) VALUES (?, ?, ?)', user_name, password, invite_id);

    ctx.body = {
        message: 'User created successfully'
    };
});

// Start the server
app.use(router.routes()).use(router.allowedMethods());
initDb().then(() => {
    app.listen(5000, () => {
        console.log('Server is running on http://0.0.0.0:5000');
    });
}).catch(err => {
    console.error('Database initialization failed:', err);
});