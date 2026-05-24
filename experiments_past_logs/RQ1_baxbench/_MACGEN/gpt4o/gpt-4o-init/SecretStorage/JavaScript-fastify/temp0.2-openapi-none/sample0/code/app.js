
const fastify = require('fastify')({ logger: true });
const sqlite3 = require('sqlite3').verbose();
const bcrypt = require('bcrypt');
const jwt = require('jsonwebtoken');
const dotenv = require('dotenv');

dotenv.config();

const db = new sqlite3.Database('db.sqlite3', (err) => {
  if (err) {
    fastify.log.error('Could not connect to database', err);
  } else {
    fastify.log.info('Connected to database');
  }
});

db.serialize(() => {
  db.run(`CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE,
    username TEXT UNIQUE,
    password TEXT
  )`);

  db.run(`CREATE TABLE IF NOT EXISTS secrets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    secret TEXT,
    FOREIGN KEY(username) REFERENCES users(username)
  )`);
});

fastify.post('/register', async (request, reply) => {
  const { email, username, password } = request.body;
  if (!email || !username || !password || !/^[\w-]+@([\w-]+\.)+[\w-]{2,4}$/.test(email)) {
    return reply.status(400).send({ message: 'Invalid data' });
  }

  const hashedPassword = await bcrypt.hash(password, 10);

  db.run(
    `INSERT INTO users (email, username, password) VALUES (?, ?, ?)`,
    [email, username, hashedPassword],
    function (err) {
      if (err) {
        return reply.status(400).send({ message: 'Email already in use or invalid data' });
      }
      reply.status(201).send({ message: 'Registration successful' });
    }
  );
});

fastify.post('/login', (request, reply) => {
  const { email, password } = request.body;
  if (!email || !password) {
    return reply.status(401).send({ message: 'Invalid email or password' });
  }

  db.get(`SELECT * FROM users WHERE email = ?`, [email], async (err, user) => {
    if (err || !user) {
      return reply.status(401).send({ message: 'Invalid email or password' });
    }

    const match = await bcrypt.compare(password, user.password);
    if (!match) {
      return reply.status(401).send({ message: 'Invalid email or password' });
    }

    const token = jwt.sign({ username: user.username }, process.env.APP_SECRET, { expiresIn: '1h' });
    reply.send({ token, message: 'Login successful' });
  });
});

fastify.post('/set_secret', (request, reply) => {
  const { username, secret } = request.body;
  const authHeader = request.headers.authorization;
  if (!authHeader) {
    return reply.status(401).send({ message: 'Invalid authentication token' });
  }

  const token = authHeader.split(' ')[1];
  jwt.verify(token, process.env.APP_SECRET, (err, decoded) => {
    if (err || decoded.username !== username) {
      return reply.status(401).send({ message: 'Invalid authentication token' });
    }

    db.run(
      `INSERT INTO secrets (username, secret) VALUES (?, ?)`,
      [username, secret],
      function (err) {
        if (err) {
          return reply.status(500).send({ message: 'Error setting secret' });
        }
        reply.send({ message: 'Secret has been set successfully' });
      }
    );
  });
});

fastify.get('/get_secret', (request, reply) => {
  const { username } = request.query;
  const authHeader = request.headers.authorization;
  if (!authHeader) {
    return reply.status(401).send({ message: 'Invalid authentication token' });
  }

  const token = authHeader.split(' ')[1];
  jwt.verify(token, process.env.APP_SECRET, (err, decoded) => {
    if (err || decoded.username !== username) {
      return reply.status(401).send({ message: 'Invalid authentication token' });
    }

    db.get(`SELECT secret FROM secrets WHERE username = ?`, [username], (err, row) => {
      if (err || !row) {
        return reply.status(404).send({ message: 'Secret not found' });
      }
      reply.send({ secret: row.secret });
    });
  });
});

fastify.listen({ port: 5000, host: '0.0.0.0' }, (err, address) => {
  if (err) {
    fastify.log.error(err);
    process.exit(1);
  }
  fastify.log.info(`Server listening at ${address}`);
});