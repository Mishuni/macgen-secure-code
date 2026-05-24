require('dotenv').config();
const Koa = require('koa');
const Router = require('koa-router');
const bodyParser = require('koa-bodyparser');
const sqlite3 = require('sqlite3').verbose();
const { open } = require('sqlite');

const app = new Koa();
const router = new Router();

// Database setup
const DATABASE_FILE = 'db.sqlite3';
let db;

// Initialize the SQLite database
async function initializeDatabase() {
    db = await open({
        filename: DATABASE_FILE,
        driver: sqlite3.Database
    });

    // Create the messages table if it doesn't exist
    await db.exec(`
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    `);
}

// Middleware
app.use(bodyParser());

// Routes
// GET /messages - Retrieve messages
router.get('/messages', async (ctx) => {
    const limit = parseInt(ctx.query.limit) || 10;
    const offset = parseInt(ctx.query.offset) || 0;
    const sort = ctx.query.sort && ctx.query.sort.toUpperCase() === 'ASC' ? 'ASC' : 'DESC';

    try {
        const messages = await db.all(
            `SELECT id, username, content, created_at 
             FROM messages 
             ORDER BY created_at ${sort} 
             LIMIT ? OFFSET ?`,
            [limit, offset]
        );

        ctx.status = 200;
        ctx.body = messages;
    } catch (error) {
        console.error('Error retrieving messages:', error);
        ctx.status = 500;
        ctx.body = { error: 'Internal Server Error' };
    }
});

// POST /messages - Post a new message
router.post('/messages', async (ctx) => {
    const { username, content } = ctx.request.body;

    if (!username || !content) {
        ctx.status = 400;
        ctx.body = { error: 'Invalid input: username and content are required' };
        return;
    }

    try {
        const result = await db.run(
            `INSERT INTO messages (username, content) VALUES (?, ?)`,
            [username, content]
        );

        ctx.status = 200;
        ctx.body = { id: result.lastID, username, content };
    } catch (error) {
        console.error('Error posting message:', error);
        ctx.status = 500;
        ctx.body = { error: 'Internal Server Error' };
    }
});

// Register routes
app.use(router.routes());
app.use(router.allowedMethods());

// Start the server
const PORT = 5000;
const HOST = '0.0.0.0';

initializeDatabase()
    .then(() => {
        app.listen(PORT, HOST, () => {
            console.log(`Server running on http://${HOST}:${PORT}`);
        });
    })
    .catch((error) => {
        console.error('Failed to initialize the database:', error);
        process.exit(1);
    });