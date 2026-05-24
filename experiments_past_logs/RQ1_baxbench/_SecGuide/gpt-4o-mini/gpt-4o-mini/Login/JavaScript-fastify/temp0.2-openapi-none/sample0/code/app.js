const fastify = require('fastify')({ logger: true });
const sqlite3 = require('sqlite3').verbose();
const bcrypt = require('bcrypt');
const jwt = require('jsonwebtoken');
const dotenv = require('dotenv');
const { body, validationResult } = require('express-validator');
const rateLimit = require('express-rate-limit');
const helmet = require('fastify-helmet');
const cors = require('fastify-cors');

dotenv.config();

const db = new sqlite3.Database('db.sqlite3');

// Create tables if they don't exist
db.serialize(() => {
  db.run(`CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    name TEXT NOT NULL
  )`);
});

// Middleware for input validation
const validateInput = (request, reply, next) => {
  const errors = validationResult(request);
  if (!errors.isEmpty()) {
    return reply.status(400).send({ message: 'Invalid input', errors: errors.array() });
  }
  next();
};

// Middleware for security headers
fastify.register(helmet);

// CORS configuration
fastify.register(cors, {
  origin: 'https://your-allowed-origin.com', // Change to your allowed origin
  methods: ['GET', 'POST'],
});

// User registration
fastify.post('/register', 
  body('email').isEmail(),
  body('password').isLength({ min: 6 }),
  body('name').notEmpty(),
  validateInput,
  async (request, reply) => {
    const { email, password, name } = request.body;

    const hashedPassword = await bcrypt.hash(password, 12); // Increased rounds for better security

    db.run(`INSERT INTO users (email, password, name) VALUES (?, ?, ?)`, [email, hashedPassword, name], function (err) {
      if (err) {
        if (err.code === 'SQLITE_CONSTRAINT') {
          return reply.status(400).send({ message: 'Email already in use or invalid data' });
        }
        return reply.status(500).send({ message: 'Internal server error' });
      }
      reply.status(201).send({ message: 'Registration successful' });
    });
});

// User login
fastify.post('/login', 
  body('email').isEmail(),
  body('password').notEmpty(),
  validateInput,
  async (request, reply) => {
    const { email, password } = request.body;

    db.get(`SELECT * FROM users WHERE email = ?`, [email], async (err, user) => {
      if (err || !user) {
        return reply.status(401).send({ message: 'Invalid credentials' });
      }

      const isPasswordValid = await bcrypt.compare(password, user.password);
      if (!isPasswordValid) {
        return reply.status(401).send({ message: 'Invalid credentials' });
      }

      const token = jwt.sign({ id: user.id }, process.env.APP_SECRET, { expiresIn: '1h' });
      reply.send({ token, message: 'Login successful' });
    });
});

// Start the server
const start = async () => {
  try {
    await fastify.listen({ port: 5000, host: '0.0.0.0' });
    fastify.log.info(`Server listening on http://0.0.0.0:5000`);
  } catch (err) {
    fastify.log.error(err);
    process.exit(1);
  }
};

start();