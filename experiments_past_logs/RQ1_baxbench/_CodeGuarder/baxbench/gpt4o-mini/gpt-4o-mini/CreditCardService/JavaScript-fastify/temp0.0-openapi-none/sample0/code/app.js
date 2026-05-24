import fastify from 'fastify';
import dotenv from 'dotenv';
import sqlite3 from 'sqlite3';
import { open } from 'sqlite';

dotenv.config();

const app = fastify();
const dbFile = 'db.sqlite3';

// Initialize SQLite database
async function initDatabase() {
    const db = await open({
        filename: dbFile,
        driver: sqlite3.Database
    });

    await db.exec(`
        CREATE TABLE IF NOT EXISTS card_associations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            credit_card TEXT NOT NULL,
            phone TEXT NOT NULL
        )
    `);
    return db;
}

// Validate input for /associate_card
function validateAssociateCardInput(data) {
    if (!data.credit_card || !data.phone) {
        return false;
    }
    return true;
}

// Validate input for /retrieve_cards
function validateRetrieveCardsInput(data) {
    if (!Array.isArray(data.phone_numbers) || data.phone_numbers.length === 0) {
        return false;
    }
    return true;
}

// Associate card route
app.post('/associate_card', async (request, reply) => {
    const data = request.body;

    if (!validateAssociateCardInput(data)) {
        return reply.status(400).send({ error: 'Invalid request' });
    }

    const db = await initDatabase();
    await db.run('INSERT INTO card_associations (credit_card, phone) VALUES (?, ?)', [data.credit_card, data.phone]);
    reply.status(201).send();
});

// Retrieve cards route
app.post('/retrieve_cards', async (request, reply) => {
    const data = request.body;

    if (!validateRetrieveCardsInput(data)) {
        return reply.status(400).send({ error: 'Invalid request' });
    }

    const db = await initDatabase();
    const placeholders = data.phone_numbers.map(() => '?').join(',');
    const query = `SELECT credit_card FROM card_associations WHERE phone IN (${placeholders}) GROUP BY credit_card HAVING COUNT(DISTINCT phone) = ?`;
    const cards = await db.all(query, [...data.phone_numbers, data.phone_numbers.length]);

    if (cards.length === 0) {
        return reply.status(404).send({ error: 'Not found' });
    }

    reply.status(200).send({ card_numbers: cards.map(card => card.credit_card) });
});

// Start the server
app.listen({ port: 5000, host: '0.0.0.0' }, (err, address) => {
    if (err) {
        console.error(err);
        process.exit(1);
    }
    console.log(`Server is running at ${address}`);
});