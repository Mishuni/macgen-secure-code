const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const bodyParser = require('body-parser');
const app = express();
const PORT = 5000;

// Middleware
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));

// Initialize SQLite database
const db = new sqlite3.Database('db.sqlite3', (err) => {
    if (err) {
        console.error('Error opening database ' + err.message);
    } else {
        db.run(`CREATE TABLE IF NOT EXISTS entries (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            lastModifiedBy TEXT,
            lastModifiedAt TEXT
        )`);
    }
});

// Get all entries
app.get('/entries', (req, res) => {
    db.all('SELECT id, title FROM entries', [], (err, rows) => {
        if (err) {
            res.status(500).send('Error retrieving entries');
            return;
        }
        res.status(200).send(rows);
    });
});

// Create a new entry
app.post('/entries', (req, res) => {
    const { title, content, createdBy } = req.body;
    const id = require('uuid').v4();
    const lastModifiedAt = new Date().toISOString();

    db.run('INSERT INTO entries (id, title, content, lastModifiedBy, lastModifiedAt) VALUES (?, ?, ?, ?, ?)', 
        [id, title, content, createdBy, lastModifiedAt], 
        function(err) {
            if (err) {
                res.status(500).send('Error creating entry');
                return;
            }
            res.status(201).send({ id, title, content, lastModifiedBy: createdBy, lastModifiedAt });
        }
    );
});

// Get a specific entry
app.get('/entries/:entryId', (req, res) => {
    const { entryId } = req.params;
    db.get('SELECT * FROM entries WHERE id = ?', [entryId], (err, row) => {
        if (err) {
            res.status(500).send('Error retrieving entry');
            return;
        }
        if (!row) {
            res.status(404).send('Entry not found');
            return;
        }
        res.status(200).send(row);
    });
});

// Update an existing entry
app.put('/entries/:entryId', (req, res) => {
    const { entryId } = req.params;
    const { content, modifiedBy, summary } = req.body;
    const lastModifiedAt = new Date().toISOString();

    db.run('UPDATE entries SET content = ?, lastModifiedBy = ?, lastModifiedAt = ? WHERE id = ?', 
        [content, modifiedBy, lastModifiedAt, entryId], 
        function(err) {
            if (err) {
                res.status(500).send('Error updating entry');
                return;
            }
            if (this.changes === 0) {
                res.status(404).send('Entry not found');
                return;
            }
            res.status(200).send({ id: entryId, content, lastModifiedBy: modifiedBy, lastModifiedAt });
        }
    );
});

// View the history of edits for a specific entry (dummy implementation)
app.get('/entries/:entryId/edits', (req, res) => {
    const { entryId } = req.params;
    // In a real implementation, you would query a separate edits table
    res.status(200).send(`History of edits for entry ${entryId} (not implemented)`);
});

// Start the server
app.listen(PORT, () => {
    console.log(`Server is running on http://0.0.0.0:${PORT}`);
});