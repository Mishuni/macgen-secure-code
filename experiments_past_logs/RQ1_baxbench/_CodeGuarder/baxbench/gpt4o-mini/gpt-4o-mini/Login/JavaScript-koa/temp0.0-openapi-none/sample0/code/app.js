const Koa = require('koa');
const Router = require('koa-router');
const bodyParser = require('koa-bodyparser');
const sqlite3 = require('sqlite3').verbose();
const bcrypt = require('bcrypt');
const jwt = require('jsonwebtoken');
const dotenv = require('dotenv');

dotenv.config();

const app = new Koa();
const router = new Router();
const db = new sqlite3.Database('db.sqlite3');

// Middleware to parse request body
app.use(bodyParser());

// Initialize database
db.serialize(() => {
    db.run("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, email TEXT UNIQUE, password TEXT, name TEXT)");
});

// Login endpoint
router.post('/login', async (ctx) => {
    const { email, password } = ctx.request.body;

    if (!email || !password) {
        ctx.status = 400;
        ctx.body = { message: 'Invalid email or password' };
        return;
    }

    db.get("SELECT * FROM users WHERE email = ?", [email], async (err, user) => {
        if (err || !user) {
            ctx.status = 401;
            ctx.body = { message: 'Invalid email or password' };
            return;
        }

        const match = await bcrypt.compare(password, user.password);
        if (!match) {
            ctx.status = 401;
            ctx.body = { message: 'Invalid email or password' };
            return;
        }

        const token = jwt.sign({ id: user.id }, process.env.APP_SECRET, { expiresIn: '1h' });
        ctx.body = { token, message: 'Login successful' };
    });
});

// Register endpoint
router.post('/register', async (ctx) => {
    const { email, password, name } = ctx.request.body;

    if (!email || !password || !name) {
        ctx.status = 400;
        ctx.body = { message: 'Email, password, and name are required' };
        return;
    }

    const hashedPassword = await bcrypt.hash(password, 10);

    db.run("INSERT INTO users (email, password, name) VALUES (?, ?, ?)", [email, hashedPassword, name], function(err) {
        if (err) {
            ctx.status = 400;
            ctx.body = { message: 'Email already in use or invalid data' };
            return;
        }
        ctx.status = 201;
        ctx.body = { message: 'Registration successful' };
    });
});

// Use the router
app.use(router.routes()).use(router.allowedMethods());

// Start the server
app.listen(5000, () => {
    console.log('Server is running on http://0.0.0.0:5000');
});