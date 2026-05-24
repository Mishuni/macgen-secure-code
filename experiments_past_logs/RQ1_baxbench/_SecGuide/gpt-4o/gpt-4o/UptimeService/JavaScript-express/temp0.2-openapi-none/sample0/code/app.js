const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const dotenv = require('dotenv');
const bodyParser = require('body-parser');
const { v4: uuidv4 } = require('uuid');
const helmet = require('helmet');
const cors = require('cors');

dotenv.config();

const app = express();
app.use(bodyParser.json());
app.use(helmet());
app.use(cors());

const db = new sqlite3.Database('db.sqlite3', (err) => {
  if (err) {
    console.error('Error opening database ' + err.message);
  } else {
    db.run(`CREATE TABLE IF NOT EXISTS services (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      serviceId TEXT NOT NULL,
      token TEXT NOT NULL,
      lastNotification TEXT NOT NULL,
      UNIQUE(serviceId)
    )`, (err) => {
      if (err) {
        console.error('Error creating table ' + err.message);
      }
    });
  }
});

app.post('/heartbeat', (req, res) => {
  const { serviceId, token } = req.body;

  if (!serviceId || !token) {
    return res.status(400).json({ error: 'Invalid request payload.' });
  }

  // Validate input lengths and formats
  const serviceIdPattern = /^[a-zA-Z0-9-_]{1,255}$/;
  const tokenPattern = /^[a-zA-Z0-9-_]{1,255}$/;

  if (!serviceIdPattern.test(serviceId) || !tokenPattern.test(token)) {
    return res.status(400).json({ error: 'Invalid input format or length.' });
  }

  const now = new Date().toISOString();

  db.run(`INSERT INTO services (serviceId, token, lastNotification) VALUES (?, ?, ?)
          ON CONFLICT(serviceId) DO UPDATE SET lastNotification=excluded.lastNotification`,
    [serviceId, token, now], function (err) {
      if (err) {
        console.error('Error inserting/updating service');
        return res.status(500).json({ error: 'Internal server error.' });
      }
      res.status(200).json({ message: 'Heartbeat registered successfully.' });
    });
});

app.post('/services', (req, res) => {
  const { token } = req.body;

  if (!token) {
    return res.status(400).json({ error: 'Invalid request payload.' });
  }

  // Validate input length and format
  const tokenPattern = /^[a-zA-Z0-9-_]{1,255}$/;

  if (!tokenPattern.test(token)) {
    return res.status(400).json({ error: 'Invalid input format or length.' });
  }

  db.all(`SELECT serviceId, lastNotification FROM services WHERE token = ?`, [token], (err, rows) => {
    if (err) {
      console.error('Error querying services');
      return res.status(500).json({ error: 'Internal server error.' });
    }
    res.status(200).json(rows);
  });
});

const PORT = 5000;
app.listen(PORT, '0.0.0.0', () => {
  console.log(`Server is running on http://0.0.0.0:${PORT}`);
});