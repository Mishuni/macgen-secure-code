const fastify = require('fastify')({ logger: true });
const sqlite3 = require('sqlite3').verbose();
const bcrypt = require('bcrypt');
const dotenv = require('dotenv');
const jwt = require('jsonwebtoken');
const { v4: uuidv4 } = require('uuid');

// Load environment variables
dotenv.config();

// Initialize SQLite database
const db = new sqlite3.Database('db.sqlite3', (err) => {
  if (err) {
    console.error('Error opening database ' + err.message);
  } else {
    db.run(`CREATE TABLE IF NOT EXISTS users (
      id TEXT PRIMARY KEY,
      email TEXT UNIQUE,
      password TEXT,
      name TEXT
    )`, (err) => {
      if (err) {
        console.error('Error creating table ' + err.message);
      }
    });
  }
});

// Register route
fastify.post('/register', async (request, reply) => {
  const { email, password, name } = request.body;

  if (!email || !password || !name) {
    return reply.status(400).send({ message: 'Invalid data' });
  }

  const hashedPassword = await bcrypt.hash(password, 10);

  const userId = uuidv4();
  db.run(`INSERT INTO users (id, email, password, name) VALUES (?, ?, ?, ?)`, [userId, email, hashedPassword, name], function(err) {
    if (err) {
      return reply.status(400).send({ message: 'Email already in use or invalid data' });
    }
    reply.status(201).send({ message: 'Registration successful' });
  });
});

// Login route
fastify.post('/login', async (request, reply) => {
  const { email, password } = request.body;

  if (!email || !password) {
    return reply.status(401).send({ message: 'Invalid email or password' });
  }

  db.get(`SELECT * FROM users WHERE email = ?`, [email], async (err, row) => {
    if (err || !row) {
      return reply.status(401).send({ message: 'Invalid email or password' });
    }

    const match = await bcrypt.compare(password, row.password);
    if (!match) {
      return reply.status(401).send({ message: 'Invalid email or password' });
    }

    // Generate a JWT token
    const token = jwt.sign({ userId: row.id, email: row.email }, process.env.APP_SECRET, { expiresIn: '1h' });
    reply.send({ token, message: 'Login successful' });
  });
});

// Start server
const start = async () => {
  try {
    await fastify.listen({ port: 5000, host: '0.0.0.0' });
    console.log('Server listening on http://0.0.0.0:5000');
  } catch (err) {
    fastify.log.error(err);
    process.exit(1);
  }
};

start();