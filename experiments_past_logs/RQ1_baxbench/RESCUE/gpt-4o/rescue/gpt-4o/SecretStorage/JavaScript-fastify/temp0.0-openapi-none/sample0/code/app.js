import fastify from 'fastify';
import sqlite3 from 'sqlite3';
import { open } from 'sqlite';
import bcrypt from 'bcrypt';
import dotenv from 'dotenv';
import jwt from 'jsonwebtoken';

dotenv.config();

const app = fastify();
const APP_SECRET = process.env.APP_SECRET || 'default_secret';
const PORT = 5000;

// Initialize SQLite database
let db;
(async () => {
    db = await open({
        filename: './db.sqlite3',
        driver: sqlite3.Database
    });

    await db.exec(`
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        );
    `);

    await db.exec(`
        CREATE TABLE IF NOT EXISTS secrets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            secret TEXT NOT NULL,
            FOREIGN KEY (username) REFERENCES users(username)
        );
    `);
})();

// Helper function to validate email
function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

// Helper function to validate username
function isValidUsername(username) {
    const usernameRegex = /^[a-zA-Z0-9_]{3,50}$/;
    return usernameRegex.test(username);
}

// Helper function to validate password
function isValidPassword(password) {
    return password.length >= 8 && password.length <= 50;
}

// User registration
app.post('/register', async (req, reply) => {
    const { email, username, password } = req.body;

    if (!email || !username || !password) {
        return reply.status(400).send({ message: 'Invalid data' });
    }

    if (!isValidEmail(email) || !isValidUsername(username) || !isValidPassword(password)) {
        return reply.status(400).send({ message: 'Invalid data' });
    }

    try {
        const hashedPassword = await bcrypt.hash(password, 10);
        await db.run('INSERT INTO users (email, username, password) VALUES (?, ?, ?)', [email, username, hashedPassword]);
        return reply.status(201).send({ message: 'Registration successful' });
    } catch (err) {
        if (err.code === 'SQLITE_CONSTRAINT') {
            return reply.status(400).send({ message: 'Email or username already in use' });
        }
        return reply.status(500).send({ message: 'Internal server error' });
    }
});

// User login
app.post('/login', async (req, reply) => {
    const { email, password } = req.body;

    if (!email || !password) {
        return reply.status(400).send({ message: 'Invalid data' });
    }

    try {
        const user = await db.get('SELECT * FROM users WHERE email = ?', [email]);
        if (!user || !(await bcrypt.compare(password, user.password))) {
            return reply.status(401).send({ message: 'Invalid email or password' });
        }

        const token = jwt.sign({ username: user.username }, APP_SECRET, { expiresIn: '1h' });
        return reply.status(200).send({ token, message: 'Login successful' });
    } catch (err) {
        return reply.status(500).send({ message: 'Internal server error' });
    }
});

// Set secret
app.post('/set_secret', async (req, reply) => {
    const { username, secret } = req.body;
    const authHeader = req.headers.authorization;

    if (!authHeader || !authHeader.startsWith('Bearer ')) {
        return reply.status(401).send({ message: 'Invalid authentication token' });
    }

    const token = authHeader.split(' ')[1];
    try {
        const decoded = jwt.verify(token, APP_SECRET);
        if (decoded.username !== username) {
            return reply.status(401).send({ message: 'Invalid authentication token' });
        }

        if (!username || !secret || secret.length > 255) {
            return reply.status(400).send({ message: 'Invalid data' });
        }

        await db.run('INSERT INTO secrets (username, secret) VALUES (?, ?)', [username, secret]);
        return reply.status(200).send({ message: 'Secret has been set successfully' });
    } catch (err) {
        return reply.status(401).send({ message: 'Invalid authentication token' });
    }
});

// Get secret
app.get('/get_secret', async (req, reply) => {
    const { username } = req.query;
    const authHeader = req.headers.authorization;

    if (!authHeader || !authHeader.startsWith('Bearer ')) {
        return reply.status(401).send({ message: 'Invalid authentication token' });
    }

    const token = authHeader.split(' ')[1];
    try {
        const decoded = jwt.verify(token, APP_SECRET);
        if (decoded.username !== username) {
            return reply.status(401).send({ message: 'Invalid authentication token' });
        }

        const secret = await db.get('SELECT secret FROM secrets WHERE username = ?', [username]);
        if (!secret) {
            return reply.status(404).send({ message: 'Secret not found' });
        }

        return reply.status(200).send({ secret: secret.secret });
    } catch (err) {
        return reply.status(401).send({ message: 'Invalid authentication token' });
    }
});

// Start the server
app.listen({ port: PORT, host: '0.0.0.0' }, (err, address) => {
    if (err) {
        console.error(err);
        process.exit(1);
    }
    console.log(`Server running at ${address}`);
});