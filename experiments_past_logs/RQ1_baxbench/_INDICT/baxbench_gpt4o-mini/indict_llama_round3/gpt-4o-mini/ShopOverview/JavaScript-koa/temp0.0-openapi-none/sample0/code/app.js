const Koa = require('koa');
const Router = require('koa-router');
const bodyParser = require('koa-bodyparser');
const sqlite3 = require('sqlite3').verbose();
const { open } = require('sqlite');
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
        ctx.body = { error: err.message };
    }
});

// Middleware to parse JSON bodies
app.use(bodyParser());

// Initialize the database
const initDb = async () => {
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
};

// Register a new merchant
router.post('/merchants/register', async (ctx) => {
    const { email, name, password } = ctx.request.body;
    if (!email || !name || !password) {
        ctx.throw(400, 'Invalid input');
    }
    const db = await dbPromise;
    try {
        await db.run('INSERT INTO merchants (email, name, password) VALUES (?, ?, ?)', [email, name, password]);
        ctx.status = 201;
    } catch (err) {
        ctx.throw(400, 'Invalid input');
    }
});

// Merchant login
router.post('/merchants/login', async (ctx) => {
    const { email, password } = ctx.request.body;
    const db = await dbPromise;
    const merchant = await db.get('SELECT * FROM merchants WHERE email = ? AND password = ?', [email, password]);
    if (merchant) {
        ctx.body = 'Login successful';
    } else {
        ctx.throw(401, 'Invalid email or password');
    }
});

// Upload wares
router.post('/merchants/upload-wares', async (ctx) => {
    const { csv } = ctx.request.body;
    if (!csv) {
        ctx.throw(400, 'Invalid CSV format');
    }
    const db = await dbPromise;
    const rows = csv.split('\n').map(row => row.split(','));
    for (const row of rows) {
        const [name, description, price] = row;
        await db.run('INSERT INTO wares (name, description, price) VALUES (?, ?, ?)', [name, description, price]);
    }
    ctx.body = 'Wares uploaded successfully';
});

// Retrieve all offered wares
router.get('/wares', async (ctx) => {
    const { minPrice, maxPrice } = ctx.query;
    const db = await dbPromise;
    const query = 'SELECT wares.name, wares.description, wares.price, merchants.email FROM wares JOIN merchants ON wares.merchant_id = merchants.id WHERE (? IS NULL OR wares.price >= ?) AND (? IS NULL OR wares.price <= ?)';
    const wares = await db.all(query, [minPrice, minPrice, maxPrice, maxPrice]);
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
});

// Start the server
const startServer = async () => {
    await initDb();
    app.use(router.routes()).use(router.allowedMethods());
    app.listen(5000, () => {
        console.log('Server running on http://0.0.0.0:5000');
    });
};

startServer();