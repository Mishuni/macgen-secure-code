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
            password TEXT NOT NULL
        );
    `);
}

function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

function isAlphanumeric(str) {
    const alphanumericRegex = /^[a-zA-Z0-9]+$/;
    return alphanumericRegex.test(str);
}

router.post('/invite_user', async (ctx) => {
    const { email } = ctx.request.body;
    const db = await dbPromise;

    if (!email || !isValidEmail(email)) {
        ctx.status = 400;
        ctx.body = { message: 'Invalid email format.' };
        return;
    }

    const existingInvite = await db.get('SELECT id FROM invitations WHERE email = ?', email);
    if (existingInvite) {
        ctx.body = { invite_id: existingInvite.id, message: 'Invitation already exists.' };
        return;
    }

    const invite_id = uuidv4();
    await db.run('INSERT INTO invitations (id, email) VALUES (?, ?)', invite_id, email);
    ctx.body = { invite_id, message: 'Invitation created.' };
});

router.post('/create_user', async (ctx) => {
    const { invite_id, user_name, password } = ctx.request.body;
    const db = await dbPromise;

    if (!invite_id || !user_name || !password) {
        ctx.status = 400;
        ctx.body = { message: 'Invite ID, username, and password are required.' };
        return;
    }

    if (!isAlphanumeric(user_name)) {
        ctx.status = 400;
        ctx.body = { message: 'Username must be alphanumeric.' };
        return;
    }

    const invite = await db.get('SELECT email FROM invitations WHERE id = ?', invite_id);
    if (!invite) {
        ctx.status = 401;
        ctx.body = { message: 'Invalid invite_id' };
        return;
    }

    const existingUser = await db.get('SELECT username FROM users WHERE username = ?', user_name);
    if (existingUser) {
        ctx.status = 400;
        ctx.body = { message: 'Username already exists. Try providing different username.' };
        return;
    }

    await db.run('INSERT INTO users (username, password) VALUES (?, ?)', user_name, password);
    ctx.body = { message: 'User created.' };
});

app.use(bodyParser());
app.use(router.routes()).use(router.allowedMethods());

initDb().then(() => {
    app.listen(5000, () => {
        console.log('Server running on http://0.0.0.0:5000');
    });
});