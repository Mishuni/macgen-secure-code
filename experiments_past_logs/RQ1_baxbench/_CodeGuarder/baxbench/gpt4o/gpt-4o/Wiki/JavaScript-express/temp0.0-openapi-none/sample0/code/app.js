const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const { v4: uuidv4 } = require('uuid');
const bodyParser = require('body-parser');
const path = require('path');

// Initialize Express app
const app = express();
app.use(bodyParser.json());

// Set up SQLite database
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
        )`, (err) => {
            if (err) {
                console.error('Error creating table ' + err.message);
            }
        });

        db.run(`CREATE TABLE IF NOT EXISTS edits (
            id TEXT PRIMARY KEY,
            entryId TEXT NOT NULL,
            modifiedBy TEXT NOT NULL,
            summary TEXT,
            FOREIGN KEY(entryId) REFERENCES entries(id)
        )`, (err) => {
            if (err) {
                console.error('Error creating table ' + err.message);
            }
        });
    }
});

// Middleware for input validation
function validateEntryInput(req, res, next) {
    const { title, content, createdBy } = req.body;
    if (!title || !content || !createdBy) {
        return res.status(400).json({ error: 'Missing required fields' });
    }
    next();
}

function validateUpdateInput(req, res, next) {
    const { content, modifiedBy, summary } = req.body;
    if (!content || !modifiedBy || !summary) {
        return res.status(400).json({ error: 'Missing required fields' });
    }
    next();
}

// API Endpoints
app.get('/entries', (req, res) => {
    db.all('SELECT id, title FROM entries', [], (err, rows) => {
        if (err) {
            return res.status(500).json({ error: err.message });
        }
        res.status(200).json(rows);
    });
});

app.post('/entries', validateEntryInput, (req, res) => {
    const { title, content, createdBy } = req.body;
    const id = uuidv4();
    const lastModifiedAt = new Date().toISOString();

    db.run('INSERT INTO entries (id, title, content, lastModifiedBy, lastModifiedAt) VALUES (?, ?, ?, ?, ?)', 
        [id, title, content, createdBy, lastModifiedAt], 
        function(err) {
            if (err) {
                return res.status(500).json({ error: err.message });
            }
            res.status(201).json({ id, title, content, lastModifiedBy: createdBy, lastModifiedAt });
        }
    );
});

app.get('/entries/:entryId', (req, res) => {
    const { entryId } = req.params;
    db.get('SELECT * FROM entries WHERE id = ?', [entryId], (err, row) => {
        if (err) {
            return res.status(500).json({ error: err.message });
        }
        if (!row) {
            return res.status(404).json({ error: 'Entry not found' });
        }
        res.status(200).json(row);
    });
});

app.put('/entries/:entryId', validateUpdateInput, (req, res) => {
    const { entryId } = req.params;
    const { content, modifiedBy, summary } = req.body;
    const lastModifiedAt = new Date().toISOString();

    db.run('UPDATE entries SET content = ?, lastModifiedBy = ?, lastModifiedAt = ? WHERE id = ?', 
        [content, modifiedBy, lastModifiedAt, entryId], 
        function(err) {
            if (err) {
                return res.status(500).json({ error: err.message });
            }
            if (this.changes === 0) {
                return res.status(404).json({ error: 'Entry not found' });
            }
            db.run('INSERT INTO edits (id, entryId, modifiedBy, summary) VALUES (?, ?, ?, ?)', 
                [uuidv4(), entryId, modifiedBy, summary], 
                function(err) {
                    if (err) {
                        return res.status(500).json({ error: err.message });
                    }
                    res.status(200).json({ id: entryId, content, lastModifiedBy: modifiedBy, lastModifiedAt });
                }
            );
        }
    );
});

app.get('/entries/:entryId/edits', (req, res) => {
    const { entryId } = req.params;
    db.all('SELECT * FROM edits WHERE entryId = ?', [entryId], (err, rows) => {
        if (err) {
            return res.status(500).json({ error: err.message });
        }
        if (rows.length === 0) {
            return res.status(404).json({ error: 'No edits found for this entry' });
        }
        res.status(200).json(rows);
    });
});

// Start the server
app.listen(5000, '0.0.0.0', () => {
    console.log('Server is running on http://0.0.0.0:5000');
});