const Koa = require('koa');
const Router = require('koa-router');
const bodyParser = require('koa-bodyparser');
const sqlite3 = require('sqlite3').verbose();
const { open } = require('sqlite');
const dotenv = require('dotenv');
const csvParser = require('csv-parser');

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
        ctx.body = { error: err.message };
    }
});

// Middleware to parse JSON bodies
app.use(bodyParser());

// Initialize the database
async function initDb() {
    const db = await dbPromise;
    await db.exec(`
        CREATE TABLE IF NOT EXISTS merchants (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            password TEXT NOT NULL
        );
    `);
    await db.exec(`
        CREATE TABLE IF NOT EXISTS wares (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT NOT NULL,
            price REAL NOT NULL,
            merchant_id INTEGER,
            FOREIGN KEY (merchant_id) REFERENCES merchants (id)
        );
    `);
}

// Register a new merchant
router.post('/merchants/register', async (ctx) => {
    const { email, name, password } = ctx.request.body;
    if (!email || !name || !password) {
        ctx.status = 400;
        ctx.body = { error: 'Invalid input' };
        return;
    }

    const db = await dbPromise;
    try {
        await db.run('INSERT INTO merchants (email, name, password) VALUES (?, ?, ?)', [email, name, password]);
        ctx.status = 201;
    } catch (err) {
        ctx.status = 400;
        ctx.body = { error: 'Invalid input' };
    }
});

// Merchant login
router.post('/merchants/login', async (ctx) => {
    const { email, password } = ctx.request.body;
    const db = await dbPromise;
    const merchant = await db.get('SELECT * FROM merchants WHERE email = ? AND password = ?', [email, password]);

    if (merchant) {
        ctx.body = 'Login successful';
        ctx.status = 200;
    } else {
        ctx.status = 401;
        ctx.body = { error: 'Invalid email or password' };
    }
});

// Upload wares
router.post('/merchants/upload-wares', async (ctx) => {
    const { csv } = ctx.request.body;
    if (!csv) {
        ctx.status = 400;
        ctx.body = { error: 'Invalid CSV format' };
        return;
    }

    const db = await dbPromise;
    const rows = [];

    // Parse CSV
    csvParser(csv, { headers: ['name', 'description', 'price'] })
        .on('data', (row) => {
            rows.push(row);
        })
        .on('end', async () => {
            const insertPromises = rows.map(row => {
                return db.run('INSERT INTO wares (name, description, price) VALUES (?, ?, ?)', [row.name, row.description, row.price]);
            });
            await Promise.all(insertPromises);
            ctx.status = 200;
            ctx.body = { message: 'Wares uploaded successfully' };
        })
        .on('error', () => {
            ctx.status = 400;
            ctx.body = { error: 'Invalid CSV format' };
        });
});

// Retrieve all offered wares
router.get('/wares', async (ctx) => {
    const { minPrice, maxPrice } = ctx.query;
    const db = await dbPromise;
    let query = 'SELECT w.name, w.description, w.price, m.email FROM wares w LEFT JOIN merchants m ON w.merchant_id = m.id';
    const params = [];

    if (minPrice) {
        query += ' WHERE w.price >= ?';
        params.push(minPrice);
    }
    if (maxPrice) {
        query += (params.length ? ' AND' : ' WHERE') + ' w.price <= ?';
        params.push(maxPrice);
    }

    const wares = await db.all(query, params);
    ctx.body = `
        <table>
            <tr>
                <th>Name</th>
                <th>Description</th>
                <th>Price</th>
                <th>Merchant Email</th>
            </tr>
            ${wares.map(ware => `
                <tr>
                    <td>${ware.name}</td>
                    <td>${ware.description}</td>
                    <td>${ware.price}</td>
                    <td>${ware.email}</td>
                </tr>
            `).join('')}
        </table>
    `;
    ctx.status = 200;
});

// Start the server
app.use(router.routes()).use(router.allowedMethods());
initDb().then(() => {
    app.listen(5000, () => {
        console.log('Server running on http://0.0.0.0:5000');
    });
});