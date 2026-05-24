import fastify from 'fastify';
import { readFileSync } from 'fs';
import { config } from 'dotenv';
import sqlite3 from 'sqlite3';
import bcrypt from 'bcrypt';
import jwt from 'jsonwebtoken';

config();

const app = fastify();
const db = new sqlite3.Database('db.sqlite3');

// Middleware to parse JSON requests
app.register(require('@fastify/cookie'));
app.register(require('@fastify/multipart'));

// Initialize database schema
db.serialize(() => {
    db.run(`CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        name TEXT NOT NULL
    )`);
});

// User registration endpoint
app.post('/register', async (request, reply) => {
    const { email, password, name } = request.body;

    if (!email || !password || !name) {
        return reply.status(400).send({ message: 'Email, password, and name are required.' });
    }

    const hashedPassword = await bcrypt.hash(password, 10);

    db.run(`INSERT INTO users (email, password, name) VALUES (?, ?, ?)`, [email, hashedPassword, name], function (err) {
        if (err) {
            if (err.code === 'SQLITE_CONSTRAINT') {
                return reply.status(400).send({ message: 'Email already in use.' });
            }
            return reply.status(500).send({ message: 'Database error.' });
        }
        reply.status(201).send({ message: 'Registration successful' });
    });
});

// User login endpoint
app.post('/login', async (request, reply) => {
    const { email, password } = request.body;

    if (!email || !password) {
        return reply.status(400).send({ message: 'Email and password are required.' });
    }

    db.get(`SELECT * FROM users WHERE email = ?`, [email], async (err, user) => {
        if (err || !user) {
            return reply.status(401).send({ message: 'Invalid email or password' });
        }

        const isValidPassword = await bcrypt.compare(password, user.password);
        if (!isValidPassword) {
            return reply.status(401).send({ message: 'Invalid email or password' });
        }

        const token = jwt.sign({ id: user.id }, process.env.APP_SECRET, { expiresIn: '1h' });
        reply.send({ token, message: 'Login successful' });
    });
});

// Start the server
app.listen(5000, '0.0.0.0', (err, address) => {
    if (err) {
        console.error(err);
        process.exit(1);
    }
    console.log(`Server is running at ${address}`);
});