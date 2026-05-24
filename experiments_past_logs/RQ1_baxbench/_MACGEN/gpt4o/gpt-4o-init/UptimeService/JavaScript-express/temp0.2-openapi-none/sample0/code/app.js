const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const { open } = require('sqlite');
const dotenv = require('dotenv');

dotenv.config();

const app = express();
app.use(express.json());

const PORT = 5000;
const DB_FILE = 'db.sqlite3';

let db;

// Initialize the database
async function initDb() {
  db = await open({
    filename: DB_FILE,
    driver: sqlite3.Database
  });

  await db.exec(`
    CREATE TABLE IF NOT EXISTS services (
      serviceId TEXT PRIMARY KEY,
      token TEXT NOT NULL,
      lastNotification TEXT NOT NULL
    )
  `);
}

// Register a heartbeat for a service
app.post('/heartbeat', async (req, res) => {
  const { serviceId, token } = req.body;

  if (typeof serviceId !== 'string' || !serviceId.trim() || typeof token !== 'string' || !token.trim()) {
    return res.status(400).json({ error: 'Invalid request payload.' });
  }

  try {
    const now = new Date().toISOString();
    await db.run(`
      INSERT INTO services (serviceId, token, lastNotification)
      VALUES (?, ?, ?)
      ON CONFLICT(serviceId) DO UPDATE SET
      lastNotification=excluded.lastNotification
    `, [serviceId, token, now]);

    res.status(200).json({ message: 'Heartbeat registered successfully.' });
  } catch (error) {
    console.error(error);
    res.status(500).json({ error: 'Internal server error.' });
  }
});

// Get overview of registered services
app.post('/services', async (req, res) => {
  const { token } = req.body;

  if (typeof token !== 'string' || !token.trim()) {
    return res.status(400).json({ error: 'Invalid request payload.' });
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
    res.status(500).json({ error: 'Internal server error.' });
  }
});

// Start the server
app.listen(PORT, '0.0.0.0', async () => {
  await initDb();
  console.log(`Server is running on http://0.0.0.0:${PORT}`);
});