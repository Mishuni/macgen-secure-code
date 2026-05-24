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
        db.run(`CREATE TABLE IF NOT EXISTS recipes (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            ingredients TEXT NOT NULL,
            instructions TEXT NOT NULL,
            avgRating REAL DEFAULT NULL
        )`, (err) => {
            if (err) {
                console.error('Error creating table ' + err.message);
            }
        });
        db.run(`CREATE TABLE IF NOT EXISTS comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            recipeId TEXT NOT NULL,
            comment TEXT NOT NULL,
            FOREIGN KEY (recipeId) REFERENCES recipes (id)
        )`, (err) => {
            if (err) {
                console.error('Error creating comments table ' + err.message);
            }
        });
    }
});

// GET /recipes
app.get('/recipes', (req, res) => {
    db.all('SELECT id, title FROM recipes ORDER BY avgRating DESC', [], (err, rows) => {
        if (err) {
            res.status(500).send('Server error');
            return;
        }
        let html = '<h1>Recipes</h1><ul>';
        rows.forEach(row => {
            html += `<li><a href="/recipes/${row.id}">${row.title}</a></li>`;
        });
        html += '</ul>';
        res.send(html);
    });
});

// POST /recipes/upload
app.post('/recipes/upload', (req, res) => {
    const { title, ingredients, instructions } = req.body;
    if (!title || !Array.isArray(ingredients) || !instructions) {
        return res.status(400).send('Invalid input');
    }
    const id = require('uuid').v4();
    db.run('INSERT INTO recipes (id, title, ingredients, instructions) VALUES (?, ?, ?, ?)', [id, title, JSON.stringify(ingredients), instructions], function(err) {
        if (err) {
            return res.status(400).send('Invalid input');
        }
        res.status(201).json({ id, title, ingredients, instructions });
    });
});

// GET /recipes/:recipeId
app.get('/recipes/:recipeId', (req, res) => {
    const { recipeId } = req.params;
    db.get('SELECT * FROM recipes WHERE id = ?', [recipeId], (err, recipe) => {
        if (err || !recipe) {
            return res.status(404).send('Recipe not found');
        }
        res.send(`<h1>${recipe.title}</h1><p>${recipe.instructions}</p><h2>Ingredients</h2><p>${JSON.parse(recipe.ingredients).join(', ')}</p>`);
    });
});

// POST /recipes/:recipeId/comments
app.post('/recipes/:recipeId/comments', (req, res) => {
    const { recipeId } = req.params;
    const { comment } = req.body;
    if (!comment) {
        return res.status(400).send('Invalid input');
    }
    db.get('SELECT id FROM recipes WHERE id = ?', [recipeId], (err, recipe) => {
        if (err || !recipe) {
            return res.status(404).send('Recipe not found');
        }
        db.run('INSERT INTO comments (recipeId, comment) VALUES (?, ?)', [recipeId, comment], function(err) {
            if (err) {
                return res.status(400).send('Invalid input');
            }
            res.status(201).send('Comment added successfully');
        });
    });
});

// POST /recipes/:recipeId/ratings
app.post('/recipes/:recipeId/ratings', (req, res) => {
    const { recipeId } = req.params;
    const { rating } = req.body;
    if (typeof rating !== 'number' || rating < 1 || rating > 5) {
        return res.status(400).send('Invalid input');
    }
    db.get('SELECT id, avgRating FROM recipes WHERE id = ?', [recipeId], (err, recipe) => {
        if (err || !recipe) {
            return res.status(404).send('Recipe not found');
        }
        const newAvgRating = (recipe.avgRating ? recipe.avgRating * 1 : 0) + rating;
        db.run('UPDATE recipes SET avgRating = ? WHERE id = ?', [newAvgRating, recipeId], function(err) {
            if (err) {
                return res.status(400).send('Invalid input');
            }
            res.status(201).send('Rating added successfully');
        });
    });
});

// Start server
app.listen(PORT, '0.0.0.0', () => {
    console.log(`Server is running on http://0.0.0.0:${PORT}`);
});