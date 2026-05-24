import express from 'express';
import sqlite3 from 'sqlite3';
import { open } from 'sqlite';
import { v4 as uuidv4 } from 'uuid';
import bcrypt from 'bcrypt';
import dotenv from 'dotenv';

dotenv.config();

const app = express();
app.use(express.json());

const dbPromise = open({
    filename: 'db.sqlite3',
    driver: sqlite3.Database
});

async function initializeDatabase() {
    const db = await dbPromise;
    await db.exec(`
        CREATE TABLE IF NOT EXISTS invitations (
            email TEXT PRIMARY KEY,
            invite_id TEXT NOT NULL
        );
    `);
    await db.exec(`
        CREATE TABLE IF NOT EXISTS users (
            user_name TEXT PRIMARY KEY,
            password TEXT NOT NULL
        );
    `);
}

app.post('/invite_user', async (req, res) => {
    const { email } = req.body;
    if (!email) {
        return res.status(400).json({ message: 'Email is required' });
    }

    const db = await dbPromise;
    const existingInvite = await db.get('SELECT invite_id FROM invitations WHERE email = ?', email);

    if (existingInvite) {
        return res.status(200).json({ invite_id: existingInvite.invite_id, message: 'Invitation already exists' });
    }

    const invite_id = uuidv4();
    await db.run('INSERT INTO invitations (email, invite_id) VALUES (?, ?)', email, invite_id);

    res.status(200).json({ invite_id, message: 'Invitation created' });
});

app.post('/create_user', async (req, res) => {
    const { invite_id, user_name, password } = req.body;
    if (!invite_id || !user_name || !password) {
        return res.status(400).json({ message: 'Invite ID, username, and password are required' });
    }

    const db = await dbPromise;
    const invite = await db.get('SELECT email FROM invitations WHERE invite_id = ?', invite_id);

    if (!invite) {
        return res.status(401).json({ message: 'Invalid invite_id' });
    }

    const existingUser = await db.get('SELECT user_name FROM users WHERE user_name = ?', user_name);
    if (existingUser) {
        return res.status(400).json({ message: 'Username already exists. Try providing different username.' });
    }

    const hashedPassword = await bcrypt.hash(password, 10);
    await db.run('INSERT INTO users (user_name, password) VALUES (?, ?)', user_name, hashedPassword);

    res.status(200).json({ message: 'User created' });
});

initializeDatabase().then(() => {
    app.listen(5000, '0.0.0.0', () => {
        console.log('Server is running on http://0.0.0.0:5000');
    });
});