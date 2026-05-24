const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const bodyParser = require('body-parser');
const { v4: uuidv4 } = require('uuid');
const app = express();
const PORT = 5000;

// Middleware
app.use(bodyParser.json());

// Database setup
const db = new sqlite3.Database('db.sqlite3', (err) => {
    if (err) {
        console.error(err.message);
    }
});

// Create tables if they don't exist
db.serialize(() => {
    db.run(`CREATE TABLE IF NOT EXISTS recipes (
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        ingredients TEXT NOT NULL,
        instructions TEXT NOT NULL,
        avgRating REAL
    )`);

    db.run(`CREATE TABLE IF NOT EXISTS comments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        recipeId TEXT NOT NULL,
        comment TEXT NOT NULL,
        FOREIGN KEY (recipeId) REFERENCES recipes(id)
    )`);

    db.run(`CREATE TABLE IF NOT EXISTS ratings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        recipeId TEXT NOT NULL,
        rating INTEGER NOT NULL CHECK(rating >= 1 AND rating <= 5),
        FOREIGN KEY (recipeId) REFERENCES recipes(id)
    )`);
});

// Routes
app.get('/recipes', (req, res) => {
    db.all(`SELECT title, id FROM recipes ORDER BY avgRating DESC`, [], (err, rows) => {
        if (err) {
            res.status(500).send('Server error');
            return;
        }
        let html = '<h1>Recipe Overview</h1><ul>';
        rows.forEach(row => {
            html += `<li><a href="/recipes/${row.id}">${row.title}</a></li>`;
        });
        html += '</ul>';
        res.status(200).send(html);
    });
});

app.post('/recipes/upload', (req, res) => {
    const { title, ingredients, instructions } = req.body;
    if (!title || !Array.isArray(ingredients) || !instructions) {
        return res.status(400).send('Invalid input');
    }
    const id = uuidv4();
    db.run(`INSERT INTO recipes (id, title, ingredients, instructions) VALUES (?, ?, ?, ?)`, [id, title, JSON.stringify(ingredients), instructions], function(err) {
        if (err) {
            return res.status(500).send('Server error');
        }
        res.status(201).json({ id, title, ingredients, instructions, avgRating: null });
    });
});

app.get('/recipes/:recipeId', (req, res) => {
    const { recipeId } = req.params;
    db.get(`SELECT * FROM recipes WHERE id = ?`, [recipeId], (err, recipe) => {
        if (err || !recipe) {
            return res.status(404).send('Recipe not found');
        }
        db.all(`SELECT comment FROM comments WHERE recipeId = ?`, [recipeId], (err, comments) => {
            if (err) {
                return res.status(500).send('Server error');
            }
            const avgRating = recipe.avgRating || 'No ratings yet';
            let html = `<h1>${recipe.title}</h1><p>${recipe.instructions}</p><h3>Ingredients</h3><ul>${JSON.parse(recipe.ingredients).map(ing => `<li>${ing}</li>`).join('')}</ul>`;
            html += `<h3>Average Rating: ${avgRating}</h3><h3>Comments</h3><ul>${comments.map(c => `<li>${c.comment}</li>`).join('')}</ul>`;
            res.status(200).send(html);
        });
    });
});

app.post('/recipes/:recipeId/comments', (req, res) => {
    const { recipeId } = req.params;
    const { comment } = req.body;
    if (!comment) {
        return res.status(400).send('Invalid input');
    }
    db.run(`INSERT INTO comments (recipeId, comment) VALUES (?, ?)`, [recipeId, comment], function(err) {
        if (err) {
            return res.status(404).send('Recipe not found');
        }
        res.status(201).send('Comment added successfully');
    });
});

app.post('/recipes/:recipeId/ratings', (req, res) => {
    const { recipeId } = req.params;
    const { rating } = req.body;
    if (!rating || rating < 1 || rating > 5) {
        return res.status(400).send('Invalid input');
    }
    db.run(`INSERT INTO ratings (recipeId, rating) VALUES (?, ?)`, [recipeId, rating], function(err) {
        if (err) {
            return res.status(404).send('Recipe not found');
        }
        db.get(`SELECT AVG(rating) as avgRating FROM ratings WHERE recipeId = ?`, [recipeId], (err, row) => {
            if (err) {
                return res.status(500).send('Server error');
            }
            db.run(`UPDATE recipes SET avgRating = ? WHERE id = ?`, [row.avgRating, recipeId]);
            res.status(201).send('Rating added successfully');
        });
    });
});

// Start server
app.listen(PORT, '0.0.0.0', () => {
    console.log(`Server is running on http://0.0.0.0:${PORT}`);
});