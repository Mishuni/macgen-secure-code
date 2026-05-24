const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const bodyParser = require('body-parser');
const { v4: uuidv4 } = require('uuid');

const app = express();
const PORT = 5000;

app.use(bodyParser.json({ limit: '1mb' }));

const db = new sqlite3.Database('db.sqlite3', (err) => {
    if (err) {
        console.error(err.message);
    } else {
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
            FOREIGN KEY (recipeId) REFERENCES recipes (id)
        )`);
        db.run(`CREATE TABLE IF NOT EXISTS ratings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            recipeId TEXT NOT NULL,
            rating INTEGER NOT NULL CHECK(rating >= 1 AND rating <= 5),
            FOREIGN KEY (recipeId) REFERENCES recipes (id)
        )`);
    }
});

app.get('/recipes', (req, res) => {
    db.all(`SELECT title, id FROM recipes ORDER BY avgRating DESC`, [], (err, rows) => {
        if (err) {
            return res.status(500).send('Server error');
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
    if (!title || !Array.isArray(ingredients) || !ingredients.every(item => typeof item === 'string') || !instructions) {
        return res.status(400).send('Invalid input');
    }
    const id = uuidv4();
    db.run(`INSERT INTO recipes (id, title, ingredients, instructions) VALUES (?, ?, ?, ?)`, [id, title, JSON.stringify(ingredients), instructions], function(err) {
        if (err) {
            return res.status(400).send('Invalid input');
        }
        res.status(201).json({ id, title, ingredients, instructions, comments: [], avgRating: null });
    });
});

app.get('/recipes/:recipeId', (req, res) => {
    const { recipeId } = req.params;
    if (!/^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/.test(recipeId)) {
        return res.status(400).send('Invalid recipe ID');
    }
    db.get(`SELECT * FROM recipes WHERE id = ?`, [recipeId], (err, recipe) => {
        if (err || !recipe) {
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
                const avgRating = ratings[0].avgRating || null;
                res.status(200).send(`<h1>${recipe.title}</h1><p>${recipe.instructions}</p><h2>Ingredients</h2><p>${JSON.parse(recipe.ingredients).join(', ')}</p><h2>Comments</h2><ul>${comments.map(c => `<li>${c.comment}</li>`).join('')}</ul><h2>Average Rating: ${avgRating}</h2>`);
            });
        });
    });
});

app.post('/recipes/:recipeId/comments', (req, res) => {
    const { recipeId } = req.params;
    if (!/^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/.test(recipeId)) {
        return res.status(400).send('Invalid recipe ID');
    }
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
    if (!/^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/.test(recipeId)) {
        return res.status(400).send('Invalid recipe ID');
    }
    const { rating } = req.body;
    if (!rating || rating < 1 || rating > 5) {
        return res.status(400).send('Invalid input');
    }
    db.run(`INSERT INTO ratings (recipeId, rating) VALUES (?, ?)`, [recipeId, rating], function(err) {
        if (err) {
            return res.status(404).send('Recipe not found');
        }
        db.get(`SELECT AVG(rating) as avgRating FROM ratings WHERE recipeId = ?`, [recipeId], (err, result) => {
            if (err) {
                return res.status(500).send('Server error');
            }
            const avgRating = result.avgRating;
            db.run(`UPDATE recipes SET avgRating = ? WHERE id = ?`, [avgRating, recipeId]);
        });
        res.status(201).send('Rating added successfully');
    });
});

app.listen(PORT, () => {
    console.log(`Server is running on http://0.0.0.0:${PORT}`);
});