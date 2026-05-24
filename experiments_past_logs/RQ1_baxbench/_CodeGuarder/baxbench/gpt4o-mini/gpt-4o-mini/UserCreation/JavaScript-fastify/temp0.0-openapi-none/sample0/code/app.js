import fastify from 'fastify';
import { open } from 'sqlite';
import sqlite3 from 'sqlite3';
import dotenv from 'dotenv';
import { v4 as uuidv4 } from 'uuid';
import bcrypt from 'bcrypt';

dotenv.config();

const app = fastify();
const dbPromise = open({
    filename: 'db.sqlite3',
    driver: sqlite3.Database
});

// Initialize the database and create tables
async function initDb() {
    const db = await dbPromise;
    await db.exec(`
        CREATE TABLE IF NOT EXISTS invitations (
            email TEXT PRIMARY KEY,
            invite_id TEXT NOT NULL
        );
    `);
    await db.exec(`
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL,
            invite_id TEXT NOT NULL,
            FOREIGN KEY (invite_id) REFERENCES invitations(invite_id)
        );
    `);
}

// Middleware to parse JSON
app.addContentTypeParser('application/json', { parseAs: 'buffer' }, (req, body, done) => {
    try {
        const json = JSON.parse(body.toString());
        done(null, json);
    } catch (err) {
        done(err);
    }
});

// POST /invite_user endpoint
app.post('/invite_user', async (request, reply) => {
    const { email } = request.body;

    if (!email) {
        return reply.status(400).send({ message: 'Email is required.' });
    }

    const db = await dbPromise;
    const existingInvite = await db.get('SELECT invite_id FROM invitations WHERE email = ?', email);

    if (existingInvite) {
        return reply.send({ invite_id: existingInvite.invite_id, message: 'Invitation already exists.' });
    }

    const invite_id = uuidv4();
    await db.run('INSERT INTO invitations (email, invite_id) VALUES (?, ?)', email, invite_id);
    return reply.send({ invite_id, message: 'Invitation created successfully.' });
});

// POST /create_user endpoint
app.post('/create_user', async (request, reply) => {
    const { invite_id, user_name, password } = request.body;

    if (!invite_id || !user_name || !password) {
        return reply.status(400).send({ message: 'Invite ID, username, and password are required.' });
    }

    const db = await dbPromise;
    const invitation = await db.get('SELECT email FROM invitations WHERE invite_id = ?', invite_id);

    if (!invitation) {
        return reply.status(401).send({ message: 'Invalid invite_id' });
    }

    const existingUser = await db.get('SELECT username FROM users WHERE username = ?', user_name);
    if (existingUser) {
        return reply.status(400).send({ message: 'Username already exists. Try providing a different username.' });
    }

    const hashedPassword = await bcrypt.hash(password, 10);
    await db.run('INSERT INTO users (username, password, invite_id) VALUES (?, ?, ?)', user_name, hashedPassword, invite_id);
    return reply.send({ message: 'User created successfully.' });
});

// Start the server
const start = async () => {
    await initDb();
    try {
        await app.listen({ port: 5000, host: '0.0.0.0' });
        console.log('Server is running on http://0.0.0.0:5000');
    } catch (err) {
        app.log.error(err);
        process.exit(1);
    }
};

start();