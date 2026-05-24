const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const bodyParser = require('body-parser');
const cookieParser = require('cookie-parser');
const bcrypt = require('bcrypt');
const { v4: uuidv4 } = require('uuid');
const dotenv = require('dotenv');
const multer = require('multer');
const csv = require('csv-parser');
const { Readable } = require('stream');
const DOMPurify = require('dompurify'); // Assuming a DOMPurify-like library is available for sanitization

dotenv.config();

const app = express();
const db = new sqlite3.Database('db.sqlite3');

app.use(bodyParser.json());
app.use(cookieParser());
app.use(express.static('public'));

db.serialize(() => {
    db.run(`CREATE TABLE IF NOT EXISTS merchants (
        id TEXT PRIMARY KEY,
        email TEXT UNIQUE,
        name TEXT,
        password TEXT
    )`);

    db.run(`CREATE TABLE IF NOT EXISTS wares (
        id TEXT PRIMARY KEY,
        merchantId TEXT,
        name TEXT,
        description TEXT,
        price REAL,
        FOREIGN KEY(merchantId) REFERENCES merchants(id)
    )`);
});

app.post('/merchants/register', async (req, res) => {
    const { email, name, password } = req.body;
    if (!email || !name || !password) {
        return res.status(400).send('Invalid input');
    }

    // Validate email format
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
        return res.status(400).send('Invalid email format');
    }

    // Validate password strength
    const passwordRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/;
    if (!passwordRegex.test(password)) {
        return res.status(400).send('Password must be at least 8 characters long and include uppercase letters, numbers, and special characters');
    }

    const id = uuidv4();
    const hashedPassword = await bcrypt.hash(password, 10); // Use async hash

    db.run(`INSERT INTO merchants (id, email, name, password) VALUES (?, ?, ?, ?)`, [id, email, name, hashedPassword], function(err) {
        if (err) {
            return res.status(400).send('Invalid input');
        }
        res.status(201).send('Merchant registered successfully');
    });
});

app.post('/merchants/login', (req, res) => {
    const { email, password } = req.body;

    db.get(`SELECT * FROM merchants WHERE email = ?`, [email], (err, row) => {
        if (err || !row || !bcrypt.compareSync(password, row.password)) {
            return res.status(401).json({ error: 'Invalid email or password' });
        }
        res.cookie('AUTH_COOKIE', row.id, { httpOnly: true, secure: true, sameSite: 'Strict' }); // Secure cookie
        res.status(200).json('Login successful');
    });
});

app.post('/merchants/upload-wares', (req, res) => {
    const merchantId = req.cookies.AUTH_COOKIE;
    if (!merchantId) {
        return res.status(401).send('Unauthorized');
    }

    const { csv: csvData } = req.body;
    const readable = Readable.from(csvData.split('\n'));

    let wares = [];
    readable.pipe(csv())
        .on('data', (data) => {
            // Validate and sanitize input data
            const price = parseFloat(data.price);
            if (isNaN(price)) {
                return res.status(400).send('Invalid price format');
            }
            const sanitizedData = {
                merchantId,
                name: DOMPurify.sanitize(data.name),
                description: DOMPurify.sanitize(data.description),
                price: price
            };
            wares.push(sanitizedData);
        })
        .on('end', () => {
            const stmt = db.prepare(`INSERT INTO wares (id, merchantId, name, description, price) VALUES (?, ?, ?, ?, ?)`);
            wares.forEach(ware => {
                stmt.run(uuidv4(), ware.merchantId, ware.name, ware.description, ware.price);
            });
            stmt.finalize();
            res.status(200).send('Wares uploaded successfully');
        })
        .on('error', () => {
            res.status(400).send('Invalid CSV format');
        });
});

app.get('/wares', (req, res) => {
    const { minPrice, maxPrice } = req.query;
    let query = `SELECT w.name, w.description, w.price, m.email FROM wares w JOIN merchants m ON w.merchantId = m.id`;
    let params = [];

    if (minPrice) {
        query += ' WHERE w.price >= ?';
        params.push(minPrice);
    }
    if (maxPrice) {
        query += (params.length ? ' AND' : ' WHERE') + ' w.price <= ?';
        params.push(maxPrice);
    }

    db.all(query, params, (err, rows) => {
        if (err) {
            return res.status(500).send('Internal Server Error');
        }

        let html = '<table><tr><th>Name</th><th>Description</th><th>Price</th><th>Merchant Email</th></tr>';
        rows.forEach(row => {
            html += `<tr><td>${DOMPurify.sanitize(row.name)}</td><td>${DOMPurify.sanitize(row.description)}</td><td>${row.price}</td><td>${DOMPurify.sanitize(row.email)}</td></tr>`;
        });
        html += '</table>';
        res.status(200).send(html);
    });
});

// Enforce HTTPS in production
app.use((req, res, next) => {
    if (req.secure) {
        return next();
    }
    res.redirect(`https://${req.headers.host}${req.url}`);
});

app.listen(5000, () => {
    console.log('Server is running on http://0.0.0.0:5000');
});