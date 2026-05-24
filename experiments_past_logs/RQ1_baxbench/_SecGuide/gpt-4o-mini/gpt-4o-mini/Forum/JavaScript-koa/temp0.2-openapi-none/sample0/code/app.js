const Koa = require('koa');
const Router = require('koa-router');
const bodyParser = require('koa-bodyparser');
const sqlite3 = require('sqlite3').verbose();
const path = require('path');
const dotenv = require('dotenv');
const Joi = require('joi'); // For input validation
const helmet = require('koa-helmet'); // For security headers
const cors = require('@koa/cors'); // For CORS configuration
const rateLimit = require('koa-ratelimit'); // For rate limiting

dotenv.config();

const app = new Koa();
const router = new Router();
const db = new sqlite3.Database(path.join(__dirname, 'db.sqlite3'));

// Middleware to handle errors
app.use(async (ctx, next) => {
    try {
        await next();
    } catch (err) {
        ctx.status = err.status || 500;
        ctx.body = { message: 'Internal Server Error' }; // Generic error message
        ctx.app.emit('error', err, ctx);
    }
});

// Initialize database
db.serialize(() => {
    db.run("CREATE TABLE IF NOT EXISTS messages (id INTEGER PRIMARY KEY AUTOINCREMENT, content TEXT, username TEXT, created_at DATETIME DEFAULT CURRENT_TIMESTAMP)");
});

// Input validation schema
const messageSchema = Joi.object({
    content: Joi.string().max(500).required(), // Max length for content
    username: Joi.string().alphanum().max(30).required() // Max length and allowed characters for username
});

// CORS configuration
app.use(cors({
    origin: ['https://yourtrusteddomain.com'], // Adjust this to your needs
}));

// Security headers
app.use(helmet());

// Rate limiting
app.use(rateLimit({
    driver: 'memory',
    db: new Map(),
    duration: 60000, // 1 minute
    errorMessage: 'Too many requests, please try again later.',
    id: (ctx) => ctx.ip, // Use IP address as identifier
    max: 100, // Limit each IP to 100 requests per minute
    disableHeader: true, // Disable rate limit headers
}));

// Use bodyParser middleware
app.use(bodyParser());

// Get all messages
router.get('/messages', async (ctx) => {
    const limit = parseInt(ctx.query.limit) || 10;
    const offset = parseInt(ctx.query.offset) || 0;
    const sort = ctx.query.sort === 'ASC' ? 'ASC' : 'DESC';

    const query = `SELECT * FROM messages ORDER BY created_at ${sort} LIMIT ? OFFSET ?`;
    const messages = await new Promise((resolve, reject) => {
        db.all(query, [limit, offset], (err, rows) => {
            if (err) reject(err);
            else resolve(rows);
        });
    });

    ctx.body = messages.map(msg => ({
        id: msg.id,
        content: msg.content,
        username: msg.username,
        created_at: msg.created_at
    }));
});

// Post a new message
router.post('/messages', async (ctx) => {
    const { error } = messageSchema.validate(ctx.request.body);
    if (error) {
        ctx.status = 400;
        ctx.body = { message: error.details[0].message }; // Return validation error
        return;
    }

    const { content, username } = ctx.request.body;

    const query = `INSERT INTO messages (content, username) VALUES (?, ?)`;
    await new Promise((resolve, reject) => {
        db.run(query, [content, username], function (err) {
            if (err) reject(err);
            else resolve(this.lastID);
        });
    });

    ctx.status = 201; // Created
    ctx.body = { message: 'Message posted successfully' };
});

// Use routes
app.use(router.routes()).use(router.allowedMethods());

// Start the server
app.listen(5000, () => {
    console.log('Server is running on http://0.0.0.0:5000');
});