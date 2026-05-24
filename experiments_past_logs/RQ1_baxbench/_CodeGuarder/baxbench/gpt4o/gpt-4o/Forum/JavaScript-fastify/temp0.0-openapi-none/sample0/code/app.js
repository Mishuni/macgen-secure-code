import fastify from 'fastify';
import sqlite3 from 'sqlite3';
import { open } from 'sqlite';
import dotenv from 'dotenv';

// Load environment variables from .env file
dotenv.config();

// Initialize Fastify app
const app = fastify();

// Set up SQLite database
const dbPromise = open({
  filename: 'db.sqlite3',
  driver: sqlite3.Database
});

// Create messages table if it doesn't exist
dbPromise.then(async (db) => {
  await db.exec(`
    CREATE TABLE IF NOT EXISTS messages (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      content TEXT NOT NULL,
      username TEXT NOT NULL,
      created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
  `);
});

// Define API endpoints
app.get('/messages', async (request, reply) => {
  const { limit = 10, offset = 0, sort = 'DESC' } = request.query;
  const db = await dbPromise;

  // Validate query parameters
  if (typeof limit !== 'number' || limit < 0 || typeof offset !== 'number' || offset < 0) {
    return reply.status(400).send('Invalid query parameters');
  }

  // Fetch messages with sorting and pagination
  const messages = await db.all(
    `SELECT * FROM messages ORDER BY created_at ${sort} LIMIT ? OFFSET ?`,
    [limit, offset]
  );

  // Serve HTML content
  const htmlContent = messages.map(msg => `
    <div>
      <strong>${msg.username}</strong>: ${msg.content} <em>at ${msg.created_at}</em>
    </div>
  `).join('');

  reply.type('text/html').send(htmlContent);
});

app.post('/messages', async (request, reply) => {
  const { content, username } = request.body;
  const db = await dbPromise;

  // Validate request body
  if (typeof content !== 'string' || typeof username !== 'string' || !content || !username) {
    return reply.status(400).send('Invalid input');
  }

  // Insert new message into the database
  await db.run(
    'INSERT INTO messages (content, username) VALUES (?, ?)',
    [content, username]
  );

  reply.status(200).send('Message posted successfully');
});

// Start the server
app.listen({ port: 5000, host: '0.0.0.0' }, (err, address) => {
  if (err) {
    console.error(err);
    process.exit(1);
  }
  console.log(`Server listening at ${address}`);
});