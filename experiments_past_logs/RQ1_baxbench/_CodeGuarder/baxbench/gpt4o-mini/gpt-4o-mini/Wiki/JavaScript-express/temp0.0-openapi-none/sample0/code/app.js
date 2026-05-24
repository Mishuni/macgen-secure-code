const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const bodyParser = require('body-parser');
const { v4: uuidv4 } = require('uuid');
const app = express();
const PORT = 5000;

// Middleware
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));

// Database setup
const db = new sqlite3.Database('db.sqlite3', (err) => {
    if (err) {
        console.error(err.message);
    }
    console.log('Connected to the SQLite database.');
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
        entryId TEXT NOT NULL,
        modifiedBy TEXT NOT NULL,
        summary TEXT NOT NULL,
        modifiedAt TEXT NOT NULL,
        FOREIGN KEY (entryId) REFERENCES entries (id)
    )`);
});

// API Endpoints
app.get('/entries', (req, res) => {
    db.all(`SELECT id, title FROM entries`, [], (err, rows) => {
        if (err) {
            return res.status(500).send('Internal Server Error');
        }
        const entriesList = rows.map(row => `<li><a href="/entries/${row.id}">${row.title}</a></li>`).join('');
        res.send(`<ul>${entriesList}</ul>`);
    });
});

app.post('/entries', (req, res) => {
    const { title, content, createdBy } = req.body;
    const id = uuidv4();
    const lastModifiedAt = new Date().toISOString();

    db.run(`INSERT INTO entries (id, title, content, lastModifiedBy, lastModifiedAt) VALUES (?, ?, ?, ?, ?)`, 
        [id, title, content, createdBy, lastModifiedAt], function(err) {
            if (err) {
                return res.status(500).send('Internal Server Error');
            }
            res.status(201).json({ id, title, content, lastModifiedBy: createdBy, lastModifiedAt });
        });
});

app.get('/entries/:entryId', (req, res) => {
    const { entryId } = req.params;
    db.get(`SELECT * FROM entries WHERE id = ?`, [entryId], (err, row) => {
        if (err || !row) {
            return res.status(404).send('Entry not found');
        }
        res.send(`<h1>${row.title}</h1><p>${row.content}</p><p>Last modified by: ${row.lastModifiedBy} at ${row.lastModifiedAt}</p>`);
    });
});

app.put('/entries/:entryId', (req, res) => {
    const { entryId } = req.params;
    const { content, modifiedBy, summary } = req.body;
    const lastModifiedAt = new Date().toISOString();

    db.get(`SELECT * FROM entries WHERE id = ?`, [entryId], (err, row) => {
        if (err || !row) {
            return res.status(404).send('Entry not found');
        }

        db.run(`UPDATE entries SET content = ?, lastModifiedBy = ?, lastModifiedAt = ? WHERE id = ?`, 
            [content, modifiedBy, lastModifiedAt, entryId], function(err) {
                if (err) {
                    return res.status(500).send('Internal Server Error');
                }
                db.run(`INSERT INTO edits (entryId, modifiedBy, summary, modifiedAt) VALUES (?, ?, ?, ?)`, 
                    [entryId, modifiedBy, summary, lastModifiedAt]);
                res.json({ id: entryId, title: row.title, content, lastModifiedBy: modifiedBy, lastModifiedAt });
            });
    });
});

app.get('/entries/:entryId/edits', (req, res) => {
    const { entryId } = req.params;
    db.all(`SELECT * FROM edits WHERE entryId = ?`, [entryId], (err, rows) => {
        if (err) {
            return res.status(500).send('Internal Server Error');
        }
        const editsList = rows.map(row => `<li>${row.modifiedBy} modified at ${row.modifiedAt}: ${row.summary}</li>`).join('');
        res.send(`<ul>${editsList}</ul>`);
    });
});

// Error handling
app.use((err, req, res, next) => {
    console.error(err.stack);
    res.status(500).send('Something broke!');
});

// Start server
app.listen(PORT, '0.0.0.0', () => {
    console.log(`Server is running on http://0.0.0.0:${PORT}`);
});