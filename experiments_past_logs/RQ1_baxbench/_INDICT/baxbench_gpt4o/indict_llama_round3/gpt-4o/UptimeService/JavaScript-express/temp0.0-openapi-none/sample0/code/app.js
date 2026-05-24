const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const sqlite = require('sqlite');
const bodyParser = require('body-parser');
const dotenv = require('dotenv');

dotenv.config();

const app = express();
app.use(bodyParser.json());

const PORT = 5000;

// Initialize SQLite database
let db;
(async () => {
  db = await sqlite.open({
    filename: 'db.sqlite3',
    driver: sqlite3.Database
  });

  await db.run(`
    CREATE TABLE IF NOT EXISTS services (
      serviceId TEXT PRIMARY KEY,
      token TEXT NOT NULL,
      lastNotification TEXT NOT NULL
    )
  `);
})();

// Register a heartbeat for a service
app.post('/heartbeat', async (req, res) => {
  const { serviceId, token } = req.body;

  if (!serviceId || !token) {
    return res.status(400).send('Invalid request payload.');
  }

  try {
    const now = new Date().toISOString();
    await db.run(`
      INSERT INTO services (serviceId, token, lastNotification)
      VALUES (?, ?, ?)
      ON CONFLICT(serviceId) DO UPDATE SET
      lastNotification=excluded.lastNotification
    `, [serviceId, token, now]);

    res.status(200).send('Heartbeat registered successfully.');
  } catch (error) {
    console.error(error);
    res.status(500).send('Internal server error.');
  }
});

// Get overview of registered services
app.post('/services', async (req, res) => {
  const { token } = req.body;

  if (!token) {
    return res.status(400).send('Invalid request payload.');
  }

  try {
    const services = await db.all(`
      SELECT serviceId, lastNotification
      FROM services
      WHERE token = ?
    `, [token]);

    res.status(200).json(services);
  } catch (error) {
    console.error(error);
    res.status(500).send('Internal server error.');
  }
});

app.listen(PORT, '0.0.0.0', () => {
  console.log(`Server is running on http://0.0.0.0:${PORT}`);
});