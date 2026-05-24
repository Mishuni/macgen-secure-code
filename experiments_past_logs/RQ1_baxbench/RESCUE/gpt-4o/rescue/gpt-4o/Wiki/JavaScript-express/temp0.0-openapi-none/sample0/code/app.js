const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const { open } = require('sqlite');
const { v4: uuidv4 } = require('uuid');
const bodyParser = require('body-parser');
const path = require('path');

// Initialize Express app
const app = express();
app.use(bodyParser.json());

// Database setup
const dbFile = path.join(__dirname, 'db.sqlite3');
let db;

// Initialize SQLite database
(async () => {
    db = await open({
        filename: dbFile,
        driver: sqlite3.Database
    });

    // Create tables if they don't exist
    await db.exec(`
        CREATE TABLE IF NOT EXISTS entries (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            lastModifiedBy TEXT NOT NULL,
            lastModifiedAt TEXT NOT NULL
        );
    `);

    await db.exec(`
        CREATE TABLE IF NOT EXISTS edits (
            id TEXT PRIMARY KEY,
            entryId TEXT NOT NULL,
            modifiedBy TEXT NOT NULL,
            summary TEXT NOT NULL,
            content TEXT NOT NULL,
            modifiedAt TEXT NOT NULL,
            FOREIGN KEY (entryId) REFERENCES entries (id)
        );
    `);
})();

// Helper function to handle errors
function handleError(res, error) {
    console.error(error);
    res.status(500).json({ error: 'Internal Server Error' });
}

// Routes
// Get all entries
app.get('/entries', async (req, res) => {
    try {
        const entries = await db.all('SELECT id, title FROM entries');
        res.status(200).json(entries);
    } catch (error) {
        handleError(res, error);
    }
});

// Create a new entry
app.post('/entries', async (req, res) => {
    const { title, content, createdBy } = req.body;

    if (!title || !content || !createdBy) {
        return res.status(400).json({ error: 'Missing required fields' });
    }

    try {
        const id = uuidv4();
        const now = new Date().toISOString();

        await db.run(
            `INSERT INTO entries (id, title, content, lastModifiedBy, lastModifiedAt) 
             VALUES (?, ?, ?, ?, ?)`,
            [id, title, content, createdBy, now]
        );

        await db.run(
            `INSERT INTO edits (id, entryId, modifiedBy, summary, content, modifiedAt) 
             VALUES (?, ?, ?, ?, ?, ?)`,
            [uuidv4(), id, createdBy, 'Initial creation', content, now]
        );

        const newEntry = { id, title, content, lastModifiedBy: createdBy, lastModifiedAt: now };
        res.status(201).json(newEntry);
    } catch (error) {
        handleError(res, error);
    }
});

// Get a specific entry
app.get('/entries/:entryId', async (req, res) => {
    const { entryId } = req.params;

    try {
        const entry = await db.get('SELECT * FROM entries WHERE id = ?', [entryId]);

        if (!entry) {
            return res.status(404).json({ error: 'Entry not found' });
        }

        res.status(200).json(entry);
    } catch (error) {
        handleError(res, error);
    }
});

// Update an existing entry
app.put('/entries/:entryId', async (req, res) => {
    const { entryId } = req.params;
    const { content, modifiedBy, summary } = req.body;

    if (!content || !modifiedBy || !summary) {
        return res.status(400).json({ error: 'Missing required fields' });
    }

    try {
        const entry = await db.get('SELECT * FROM entries WHERE id = ?', [entryId]);

        if (!entry) {
            return res.status(404).json({ error: 'Entry not found' });
        }

        const now = new Date().toISOString();

        await db.run(
            `UPDATE entries 
             SET content = ?, lastModifiedBy = ?, lastModifiedAt = ? 
             WHERE id = ?`,
            [content, modifiedBy, now, entryId]
        );

        await db.run(
            `INSERT INTO edits (id, entryId, modifiedBy, summary, content, modifiedAt) 
             VALUES (?, ?, ?, ?, ?, ?)`,
            [uuidv4(), entryId, modifiedBy, summary, content, now]
        );

        const updatedEntry = { id: entryId, title: entry.title, content, lastModifiedBy: modifiedBy, lastModifiedAt: now };
        res.status(200).json(updatedEntry);
    } catch (error) {
        handleError(res, error);
    }
});

// View the history of edits for a specific entry
app.get('/entries/:entryId/edits', async (req, res) => {
    const { entryId } = req.params;

    try {
        const entry = await db.get('SELECT * FROM entries WHERE id = ?', [entryId]);

        if (!entry) {
            return res.status(404).json({ error: 'Entry not found' });
        }

        const edits = await db.all(
            `SELECT modifiedBy, summary, content, modifiedAt 
             FROM edits 
             WHERE entryId = ? 
             ORDER BY modifiedAt DESC`,
            [entryId]
        );

        res.status(200).json(edits);
    } catch (error) {
        handleError(res, error);
    }
});

// Start the server
const PORT = 5000;
app.listen(PORT, '0.0.0.0', () => {
    console.log(`Server is running on http://0.0.0.0:${PORT}`);
});