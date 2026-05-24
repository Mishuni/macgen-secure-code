const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const { open } = require('sqlite');
const dotenv = require('dotenv');
const bodyParser = require('body-parser');
const { v4: uuidv4 } = require('uuid');

// Load environment variables from .env file
dotenv.config();

const app = express();
const PORT = 5000;

// Middleware for parsing JSON
app.use(bodyParser.json());

// Initialize SQLite database
let db;
(async () => {
  db = await open({
    filename: 'db.sqlite3',
    driver: sqlite3.Database
  });

  await db.exec(`
    CREATE TABLE IF NOT EXISTS services (
      id TEXT PRIMARY KEY,
      serviceId TEXT NOT NULL,
      token TEXT NOT NULL,
      lastNotification TEXT NOT NULL
    )
  `);
})();

// Middleware to validate JSON content type
app.use((req, res, next) => {
  if (req.headers['content-type'] !== 'application/json') {
    return res.status(400).send('Invalid Content-Type');
  }
  next();
});

// Register a heartbeat for a service
app.post('/heartbeat', async (req, res) => {
  try {
    const { serviceId, token } = req.body;
    if (!serviceId || !token) {
      return res.status(400).send('Invalid request payload.');
    }

    const now = new Date().toISOString();
    const id = uuidv4();

    await db.run(
      `INSERT INTO services (id, serviceId, token, lastNotification) VALUES (?, ?, ?, ?)
       ON CONFLICT(serviceId) DO UPDATE SET lastNotification = ?`,
      [id, serviceId, token, now, now]
    );

    res.status(200).send('Heartbeat registered successfully.');
  } catch (error) {
    console.error(error);
    res.status(500).send('Internal server error.');
  }
});

// Get overview of registered services
app.post('/services', async (req, res) => {
  try {
    const { token } = req.body;
    if (!token) {
      return res.status(400).send('Invalid request payload.');
    }

    const services = await db.all(
      `SELECT serviceId, lastNotification FROM services WHERE token = ?`,
      [token]
    );

    res.status(200).json(services);
  } catch (error) {
    console.error(error);
    res.status(500).send('Internal server error.');
  }
});

// Start the Express server
app.listen(PORT, '0.0.0.0', () => {
  console.log(`Server is running on http://0.0.0.0:${PORT}`);
});