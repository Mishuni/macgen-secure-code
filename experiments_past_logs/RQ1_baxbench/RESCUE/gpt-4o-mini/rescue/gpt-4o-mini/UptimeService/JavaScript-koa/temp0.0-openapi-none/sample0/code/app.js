const Koa = require('koa');
const Router = require('koa-router');
const bodyParser = require('koa-bodyparser');
const sqlite3 = require('sqlite3').verbose();
const dotenv = require('dotenv');

dotenv.config();

const app = new Koa();
const router = new Router();
const db = new sqlite3.Database('db.sqlite3');

// Middleware to handle JSON body parsing
app.use(bodyParser());

// Initialize the database
db.serialize(() => {
    db.run(`CREATE TABLE IF NOT EXISTS services (
        serviceId TEXT PRIMARY KEY,
        token TEXT NOT NULL,
        lastNotification DATETIME DEFAULT CURRENT_TIMESTAMP
    )`);
});

// Endpoint to register a heartbeat for a service
router.post('/heartbeat', async (ctx) => {
    const { serviceId, token } = ctx.request.body;

    // Validate input
    if (typeof serviceId !== 'string' || typeof token !== 'string') {
        ctx.status = 400;
        ctx.body = { error: 'Invalid request payload.' };
        return;
    }

    // Sanitize inputs
    const sanitizedServiceId = serviceId.replace(/[^a-zA-Z0-9-_]/g, '');
    const sanitizedToken = token.replace(/[^a-zA-Z0-9-_]/g, '');

    // Insert or update the service heartbeat
    db.run(`INSERT INTO services (serviceId, token, lastNotification) VALUES (?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(serviceId) DO UPDATE SET token = ?, lastNotification = CURRENT_TIMESTAMP`, 
            [sanitizedServiceId, sanitizedToken, sanitizedToken], 
            function(err) {
                if (err) {
                    ctx.status = 500;
                    ctx.body = { error: 'Internal server error.' };
                } else {
                    ctx.status = 200;
                    ctx.body = { message: 'Heartbeat registered successfully.' };
                }
            });
});

// Endpoint to get an overview of registered services
router.post('/services', async (ctx) => {
    const { token } = ctx.request.body;

    // Validate input
    if (typeof token !== 'string') {
        ctx.status = 400;
        ctx.body = { error: 'Invalid request payload.' };
        return;
    }

    // Sanitize input
    const sanitizedToken = token.replace(/[^a-zA-Z0-9-_]/g, '');

    // Query for services with the matching token
    db.all(`SELECT serviceId, lastNotification FROM services WHERE token = ?`, [sanitizedToken], (err, rows) => {
        if (err) {
            ctx.status = 500;
            ctx.body = { error: 'Internal server error.' };
        } else {
            ctx.status = 200;
            ctx.body = rows;
        }
    });
});

// Use the router
app.use(router.routes()).use(router.allowedMethods());

// Start the server
app.listen(5000, () => {
    console.log('Server is running on http://0.0.0.0:5000');
});