const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const bodyParser = require('body-parser');
const { escape } = require('html-entities'); // Importing html-entities for escaping
const { v4: uuidv4 } = require('uuid'); // Importing UUID for generating unique IDs
const app = express();
const PORT = 5000;

// Middleware
app.use(bodyParser.json());

// Database setup
const db = new sqlite3.Database('db.sqlite3', (err) => {
    if (err) {
        console.error(err.message);
    }
    console.log('Connected to the SQLite database.');
});

// Create tables if they don't exist
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
        FOREIGN KEY (recipeId) REFERENCES recipes(id)
    )`);

    db.run(`CREATE TABLE IF NOT EXISTS ratings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        recipeId TEXT NOT NULL,
        rating INTEGER NOT NULL CHECK(rating >= 1 AND rating <= 5),
        FOREIGN KEY (recipeId) REFERENCES recipes(id)
    )`);
});

// Input validation function for recipeId
const isValidRecipeId = (id) => {
    const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
    return uuidRegex.test(id);
};

// Routes
app.get('/recipes', (req, res) => {
    db.all(`SELECT title, id FROM recipes`, [], (err, rows) => {
        if (err) {
            res.status(500).send('Server error');
            return;
        }
        let html = '<h1>Recipe Overview</h1><ul>';
        rows.forEach(row => {
            html += `<li><a href="/recipes/${escape(row.id)}">${escape(row.title)}</a></li>`;
        });
        html += '</ul>';
        res.status(200).send(html);
    });
});

app.post('/recipes/upload', (req, res) => {
    const { title, ingredients, instructions } = req.body;
    const id = uuidv4();
    
    // Input validation
    if (!title || typeof title !== 'string' || title.length > 100 ||
        !ingredients || !Array.isArray(ingredients) || ingredients.length === 0 ||
        !instructions || typeof instructions !== 'string' || instructions.length > 500) {
        return res.status(400).send('Invalid input');
    }

    db.run(`INSERT INTO recipes (id, title, ingredients, instructions) VALUES (?, ?, ?, ?)`, 
        [id, title, JSON.stringify(ingredients), instructions], function(err) {
        if (err) {
            return res.status(500).send('Server error');
        }
        res.status(201).json({ id, title, ingredients, instructions });
    });
});

app.get('/recipes/:recipeId', (req, res) => {
    const { recipeId } = req.params;

    // Validate recipeId
    if (!isValidRecipeId(recipeId)) {
        return res.status(400).send('Invalid recipe ID format');
    }

    db.get(`SELECT title, ingredients, instructions FROM recipes WHERE id = ?`, [recipeId], (err, row) => {
        if (err || !row) {
            return res.status(404).send('Recipe not found');
        }
        res.status(200).send(`<h1>${escape(row.title)}</h1><p>Ingredients: ${escape(JSON.parse(row.ingredients).join(', '))}</p><p>Instructions: ${escape(row.instructions)}</p>`);
    });
});

app.post('/recipes/:recipeId/comments', (req, res) => {
    const { recipeId } = req.params;
    const { comment } = req.body;

    // Validate recipeId
    if (!isValidRecipeId(recipeId)) {
        return res.status(400).send('Invalid recipe ID format');
    }

    // Input validation
    if (!comment || typeof comment !== 'string' || comment.length > 300) {
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

    // Validate recipeId
    if (!isValidRecipeId(recipeId)) {
        return res.status(400).send('Invalid recipe ID format');
    }

    // Input validation
    if (!rating || typeof rating !== 'number' || rating < 1 || rating > 5) {
        return res.status(400).send('Invalid input');
    }

    db.run(`INSERT INTO ratings (recipeId, rating) VALUES (?, ?)`, [recipeId, rating], function(err) {
        if (err) {
            return res.status(404).send('Recipe not found');
        }
        res.status(201).send('Rating added successfully');
    });
});

// Start server
app.listen(PORT, '0.0.0.0', () => {
    console.log(`Server is running on http://0.0.0.0:${PORT}`);
});