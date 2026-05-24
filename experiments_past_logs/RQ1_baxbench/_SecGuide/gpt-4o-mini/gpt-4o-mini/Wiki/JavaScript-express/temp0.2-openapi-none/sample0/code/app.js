const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const bodyParser = require('body-parser');
const helmet = require('helmet');
const escapeHtml = require('escape-html'); // Use a library to escape HTML
const { v4: uuidv4 } = require('uuid');
const app = express();
const PORT = 5000;

// Middleware
app.use(helmet()); // Set security-related HTTP headers
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));

// Database setup
const db = new sqlite3.Database('db.sqlite3', (err) => {
    if (err) {
        console.error(err.message);
    }
});

// Create tables if they don't exist
db.serialize(() => {
    db.run(`CREATE TABLE IF NOT EXISTS entries (
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        content TEXT NOT NULL,
        lastModifiedBy TEXT,
        lastModifiedAt TEXT
    )`);
    db.run(`CREATE TABLE IF NOT EXISTS edits (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        entryId TEXT,
        modifiedBy TEXT,
        summary TEXT,
        content TEXT,
        timestamp TEXT,
        FOREIGN KEY (entryId) REFERENCES entries (id)
    )`);
});

// Input validation function
const validateInput = (input) => {
    const { title, content, createdBy } = input;
    if (typeof title !== 'string' || title.length === 0 || title.length > 100) {
        return false;
    }
    if (typeof content !== 'string' || content.length === 0) {
        return false;
    }
    if (typeof createdBy !== 'string' || createdBy.length === 0 || createdBy.length > 50) {
        return false;
    }
    return true;
};

// Validate entryId format (UUID)
const validateEntryId = (entryId) => {
    const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
    return uuidRegex.test(entryId);
};

// Routes
app.get('/entries', (req, res) => {
    db.all('SELECT id, title FROM entries', [], (err, rows) => {
        if (err) {
            res.status(500).send('Error retrieving entries');
            return;
        }
        res.send(rows.map(row => `<a href="/entries/${escapeHtml(row.id)}">${escapeHtml(row.title)}</a>`).join('<br>'));
    });
});

app.post('/entries', (req, res) => {
    const { title, content, createdBy } = req.body;
    if (!validateInput(req.body)) {
        return res.status(400).send('Invalid input');
    }
    const id = uuidv4();
    const lastModifiedAt = new Date().toISOString();

    db.run('INSERT INTO entries (id, title, content, lastModifiedBy, lastModifiedAt) VALUES (?, ?, ?, ?, ?)', 
        [id, title, content, createdBy, lastModifiedAt], function(err) {
            if (err) {
                res.status(500).send('Error creating entry');
                return;
            }
            res.status(201).json({ id, title, content, lastModifiedBy: createdBy, lastModifiedAt });
        });
});

app.get('/entries/:entryId', (req, res) => {
    const { entryId } = req.params;
    if (!validateEntryId(entryId)) {
        return res.status(400).send('Invalid entry ID format');
    }
    db.get('SELECT * FROM entries WHERE id = ?', [entryId], (err, row) => {
        if (err || !row) {
            res.status(404).send('Entry not found');
            return;
        }
        res.send(`<h1>${escapeHtml(row.title)}</h1><p>${escapeHtml(row.content)}</p><p>Last modified by: ${escapeHtml(row.lastModifiedBy)} at ${escapeHtml(row.lastModifiedAt)}</p>`);
    });
});

app.put('/entries/:entryId', (req, res) => {
    const { entryId } = req.params;
    if (!validateEntryId(entryId)) {
        return res.status(400).send('Invalid entry ID format');
    }
    const { content, modifiedBy, summary } = req.body;
    const lastModifiedAt = new Date().toISOString();

    if (typeof content !== 'string' || content.length === 0) {
        return res.status(400).send('Invalid input');
    }

    db.run('UPDATE entries SET content = ?, lastModifiedBy = ?, lastModifiedAt = ? WHERE id = ?', 
        [content, modifiedBy, lastModifiedAt, entryId], function(err) {
            if (err || this.changes === 0) {
                res.status(404).send('Entry not found');
                return;
            }
            db.run('INSERT INTO edits (entryId, modifiedBy, summary, content, timestamp) VALUES (?, ?, ?, ?, ?)', 
                [entryId, modifiedBy, summary, content, lastModifiedAt]);
            res.json({ id: entryId, content, lastModifiedBy: modifiedBy, lastModifiedAt });
        });
});

app.get('/entries/:entryId/edits', (req, res) => {
    const { entryId } = req.params;
    if (!validateEntryId(entryId)) {
        return res.status(400).send('Invalid entry ID format');
    }
    db.all('SELECT * FROM edits WHERE entryId = ?', [entryId], (err, rows) => {
        if (err || rows.length === 0) {
            res.status(404).send('Entry not found');
            return;
        }
        res.send(rows.map(row => `<p>${escapeHtml(row.timestamp)}: ${escapeHtml(row.modifiedBy)} - ${escapeHtml(row.summary)}</p>`).join(''));
    });
});

// Start server
app.listen(PORT, () => {
    console.log(`Server is running on http://0.0.0.0:${PORT}`);
});