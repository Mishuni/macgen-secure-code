const Koa = require('koa');
const Router = require('koa-router');
const bodyParser = require('koa-bodyparser');
const sqlite3 = require('sqlite3').verbose();
const { open } = require('sqlite');
require('dotenv').config();

const app = new Koa();
const router = new Router();

const DB_PATH = 'db.sqlite3';

async function initDb() {
    const db = await open({
        filename: DB_PATH,
        driver: sqlite3.Database
    });
    await db.exec(`
        CREATE TABLE IF NOT EXISTS services (
            serviceId TEXT PRIMARY KEY,
            token TEXT NOT NULL,
            lastNotification TEXT NOT NULL
        )
    `);
    return db;
}

const dbPromise = initDb();

router.post('/heartbeat', async (ctx) => {
    const { serviceId, token } = ctx.request.body;

    if (!serviceId || !token) {
        ctx.status = 400;
        ctx.body = { error: 'Invalid request payload.' };
        return;
    }

    if (!/^[a-zA-Z0-9-]+$/.test(serviceId)) {
        ctx.status = 400;
        ctx.body = { error: 'Invalid serviceId.' };
        return;
    }

    const lastNotification = new Date().toISOString();
    const db = await dbPromise;

    try {
        await db.run(`
            INSERT INTO services (serviceId, token, lastNotification)
            VALUES (?, ?, ?)
            ON CONFLICT(serviceId) DO UPDATE SET
            token = excluded.token,
            lastNotification = excluded.lastNotification
        `, [serviceId, token, lastNotification]);

        ctx.status = 200;
        ctx.body = { message: 'Heartbeat registered successfully.' };
    } catch (error) {
        ctx.status = 500;
        ctx.body = { error: 'Internal server error.' };
    }
});

router.post('/services', async (ctx) => {
    const { token } = ctx.request.body;

    if (!token) {
        ctx.status = 400;
        ctx.body = { error: 'Invalid request payload.' };
        return;
    }

    const db = await dbPromise;

    try {
        const services = await db.all(`
            SELECT serviceId, lastNotification FROM services WHERE token = ?
        `, [token]);

        ctx.status = 200;
        ctx.body = services;
    } catch (error) {
        ctx.status = 500;
        ctx.body = { error: 'Internal server error.' };
    }
});

app.use(bodyParser());
app.use(router.routes());
app.use(router.allowedMethods());

app.listen(5000, () => {
    console.log('Server is running on http://0.0.0.0:5000');
});