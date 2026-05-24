const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const bodyParser = require('body-parser');

const app = express();
const PORT = 5000;

// Middleware
app.use(bodyParser.json());

// Initialize SQLite database
const db = new sqlite3.Database('db.sqlite3', (err) => {
    if (err) {
        console.error(err.message);
    }
    console.log('Connected to the SQLite database.');
});

// Create tables if they do not exist
db.serialize(() => {
    db.run(`CREATE TABLE IF NOT EXISTS recipes (
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        ingredients TEXT NOT NULL,
        instructions TEXT NOT NULL
    )`);

    db.run(`CREATE TABLE IF NOT EXISTS comments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        recipeId TEXT NOT NULL,
        comment TEXT NOT NULL,
        FOREIGN KEY (recipeId) REFERENCES recipes (id)
    )`);

    db.run(`CREATE TABLE IF NOT EXISTS ratings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        recipeId TEXT NOT NULL,
        rating INTEGER NOT NULL CHECK(rating >= 1 AND rating <= 5),
        FOREIGN KEY (recipeId) REFERENCES recipes (id)
    )`);
});

// Get overview of recipes
app.get('/recipes', (req, res) => {
    db.all(`SELECT id, title FROM recipes`, [], (err, rows) => {
        if (err) {
            return res.status(500).send('Server error');
        }
        res.send(rows);
    });
});

// Upload a new recipe
app.post('/recipes/upload', (req, res) => {
    const { title, ingredients, instructions } = req.body;
    const id = require('uuid').v4();

    if (!title || !ingredients || !instructions) {
        return res.status(400).send('Invalid input');
    }

    db.run(`INSERT INTO recipes (id, title, ingredients, instructions) VALUES (?, ?, ?, ?)`, 
        [id, title, JSON.stringify(ingredients), instructions], 
        function(err) {
            if (err) {
                return res.status(500).send('Server error');
            }
            res.status(201).json({ id, title, ingredients, instructions });
        }
    );
});

// Get a recipe by ID
app.get('/recipes/:recipeId', (req, res) => {
    const recipeId = req.params.recipeId;

    db.get(`SELECT * FROM recipes WHERE id = ?`, [recipeId], (err, recipe) => {
        if (err) {
            return res.status(500).send('Server error');
        }
        if (!recipe) {
            return res.status(404).send('Recipe not found');
        }

        db.all(`SELECT comment FROM comments WHERE recipeId = ?`, [recipeId], (err, comments) => {
            if (err) {
                return res.status(500).send('Server error');
            }

            db.all(`SELECT AVG(rating) as avgRating FROM ratings WHERE recipeId = ?`, [recipeId], (err, ratings) => {
                if (err) {
                    return res.status(500).send('Server error');
                }

                const avgRating = ratings[0] ? ratings[0].avgRating : null;
                res.json({ ...recipe, comments, avgRating });
            });
        });
    });
});

// Add a comment to a recipe
app.post('/recipes/:recipeId/comments', (req, res) => {
    const recipeId = req.params.recipeId;
    const { comment } = req.body;

    if (!comment) {
        return res.status(400).send('Invalid input');
    }

    db.run(`INSERT INTO comments (recipeId, comment) VALUES (?, ?)`, [recipeId, comment], function(err) {
        if (err) {
            return res.status(500).send('Server error');
        }
        res.status(201).send('Comment added successfully');
    });
});

// Rate a recipe
app.post('/recipes/:recipeId/ratings', (req, res) => {
    const recipeId = req.params.recipeId;
    const { rating } = req.body;

    if (typeof rating !== 'number' || rating < 1 || rating > 5) {
        return res.status(400).send('Invalid input');
    }

    db.run(`INSERT INTO ratings (recipeId, rating) VALUES (?, ?)`, [recipeId, rating], function(err) {
        if (err) {
            return res.status(500).send('Server error');
        }
        res.status(201).send('Rating added successfully');
    });
});

// Start the server
app.listen(PORT, () => {
    console.log(`Server is running on http://0.0.0.0:${PORT}`);
});