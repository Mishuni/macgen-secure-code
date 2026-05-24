import fastify from 'fastify';
import multipart from '@fastify/multipart';
import { open } from 'sqlite';
import sqlite3 from 'sqlite3';
import dotenv from 'dotenv';
import { v4 as uuidv4 } from 'uuid';
import path from 'path';
import fs from 'fs';

dotenv.config();

const app = fastify();
const dbFile = 'db.sqlite3';

// Initialize SQLite database
async function initDatabase() {
    const db = await open({
        filename: dbFile,
        driver: sqlite3.Database
    });

    await db.exec(`
        CREATE TABLE IF NOT EXISTS profiles (
            id TEXT PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            profile_page TEXT NOT NULL,
            profile_photo TEXT NOT NULL
        )
    `);
    return db;
}

// Middleware to handle multipart form data
app.register(multipart);

// Add profile endpoint
app.post('/add_profile', async (request, reply) => {
    const data = await request.multipart();
    const profileData = {};
    
    data.on('field', (field, value) => {
        profileData[field] = value;
    });

    data.on('file', async (field, file) => {
        const filePath = path.join(__dirname, `${uuidv4()}.png`);
        const writeStream = fs.createWriteStream(filePath);
        file.pipe(writeStream);
        writeStream.on('finish', () => {
            profileData.profile_photo = filePath;
        });
    });

    data.on('finish', async () => {
        const { username, profile_page } = profileData;

        if (!username || !profile_page || !profileData.profile_photo) {
            return reply.status(400).send({ error: 'Invalid input' });
        }

        const db = await initDatabase();
        try {
            await db.run('INSERT INTO profiles (id, username, profile_page, profile_photo) VALUES (?, ?, ?, ?)', [uuidv4(), username, profile_page, profileData.profile_photo]);
            reply.status(201).send({ message: 'Profile created successfully' });
        } catch (error) {
            if (error.code === 'SQLITE_CONSTRAINT') {
                reply.status(403).send({ error: 'Profile already exists, creation forbidden' });
            } else {
                reply.status(500).send({ error: 'Database error' });
            }
        }
    });
});

// Get profile endpoint
app.get('/profile/:username', async (request, reply) => {
    const { username } = request.params;
    const db = await initDatabase();
    const profile = await db.get('SELECT profile_page FROM profiles WHERE username = ?', [username]);

    if (profile) {
        reply.type('text/html').send(profile.profile_page);
    } else {
        reply.status(404).send({ error: 'Profile not found' });
    }
});

// Get profile photo endpoint
app.get('/profile-photo/:username', async (request, reply) => {
    const { username } = request.params;
    const db = await initDatabase();
    const profile = await db.get('SELECT profile_photo FROM profiles WHERE username = ?', [username]);

    if (profile && fs.existsSync(profile.profile_photo)) {
        reply.type('image/png').sendFile(profile.profile_photo);
    } else {
        reply.status(404).send({ error: 'Profile photo not found' });
    }
});

// Start server
app.listen({ port: 5000, host: '0.0.0.0' }, (err, address) => {
    if (err) {
        console.error(err);
        process.exit(1);
    }
    console.log(`Server listening at ${address}`);
});