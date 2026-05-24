const Koa = require('koa');
const Router = require('koa-router');
const bodyParser = require('koa-bodyparser');
const sqlite3 = require('sqlite3').verbose();
const { open } = require('sqlite');
require('dotenv').config();

const app = new Koa();
const router = new Router();

// Initialize SQLite database
let db;
(async () => {
    db = await open({
        filename: 'db.sqlite3',
        driver: sqlite3.Database
    });
    await db.exec(`CREATE TABLE IF NOT EXISTS services (
        serviceId TEXT PRIMARY KEY,
        token TEXT NOT NULL,
        lastNotification DATETIME DEFAULT CURRENT_TIMESTAMP
    )`);
})();

// Middleware
app.use(bodyParser());

// Register a heartbeat for a service
router.post('/heartbeat', async (ctx) => {
    const { serviceId, token } = ctx.request.body;

    if (!serviceId || !token) {
        ctx.status = 400;
        ctx.body = { error: 'Invalid request payload.' };
        return;
    }

    try {
        await db.run(`INSERT OR REPLACE INTO services (serviceId, token, lastNotification) VALUES (?, ?, CURRENT_TIMESTAMP)`, [serviceId, token]);
        ctx.status = 200;
        ctx.body = { message: 'Heartbeat registered successfully.' };
    } catch (error) {
        ctx.status = 500;
        ctx.body = { error: 'Internal server error.' };
    }
});

// Get overview of registered services
router.post('/services', async (ctx) => {
    const { token } = ctx.request.body;

    if (!token) {
        ctx.status = 400;
        ctx.body = { error: 'Invalid request payload.' };
        return;
    }

    try {
        const services = await db.all(`SELECT serviceId, lastNotification FROM services WHERE token = ?`, [token]);
        ctx.status = 200;
        ctx.body = services;
    } catch (error) {
        ctx.status = 500;
        ctx.body = { error: 'Internal server error.' };
    }
});

// Use the router
app.use(router.routes()).use(router.allowedMethods());

// Start the server
app.listen(5000, () => {
    console.log('Server is running on http://0.0.0.0:5000');
});