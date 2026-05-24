const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const bodyParser = require('body-parser');
const { v4: uuidv4 } = require('uuid');

const app = express();
const db = new sqlite3.Database('db.sqlite3');

app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: false }));

db.serialize(() => {
    db.run("CREATE TABLE IF NOT EXISTS entries (id TEXT PRIMARY KEY, title TEXT, content TEXT, lastModifiedBy TEXT, lastModifiedAt TEXT)");
});

app.get('/entries', (req, res) => {
    db.all("SELECT id, title FROM entries", [], (err, rows) => {
        if (err) {
            return res.status(500).send('Internal Server Error');
        }
        res.status(200).json(rows);
    });
});

app.post('/entries', (req, res) => {
    const { title, content, createdBy } = req.body;
    const id = uuidv4();
    const lastModifiedAt = new Date().toISOString();

    db.run("INSERT INTO entries (id, title, content, lastModifiedBy, lastModifiedAt) VALUES (?, ?, ?, ?, ?)", 
        [id, title, content, createdBy, lastModifiedAt], 
        function(err) {
            if (err) {
                return res.status(500).send('Internal Server Error');
            }
            res.status(201).json({ id, title, content, lastModifiedBy: createdBy, lastModifiedAt });
        });
});

app.get('/entries/:entryId', (req, res) => {
    const { entryId } = req.params;
    db.get("SELECT * FROM entries WHERE id = ?", [entryId], (err, row) => {
        if (err) {
            return res.status(500).send('Internal Server Error');
        }
        if (!row) {
            return res.status(404).send('Entry not found');
        }
        res.status(200).json(row);
    });
});

app.put('/entries/:entryId', (req, res) => {
    const { entryId } = req.params;
    const { content, modifiedBy, summary } = req.body;
    const lastModifiedAt = new Date().toISOString();

    db.run("UPDATE entries SET content = ?, lastModifiedBy = ?, lastModifiedAt = ? WHERE id = ?", 
        [content, modifiedBy, lastModifiedAt, entryId], 
        function(err) {
            if (err) {
                return res.status(500).send('Internal Server Error');
            }
            if (this.changes === 0) {
                return res.status(404).send('Entry not found');
            }
            res.status(200).json({ message: 'Entry updated successfully' });
        });
});

app.get('/entries/:entryId/edits', (req, res) => {
    const { entryId } = req.params;
    // Placeholder for edit history retrieval logic
    res.status(200).send('Edit history not implemented');
});

app.listen(5000, () => {
    console.log('Server is running on http://0.0.0.0:5000');
});