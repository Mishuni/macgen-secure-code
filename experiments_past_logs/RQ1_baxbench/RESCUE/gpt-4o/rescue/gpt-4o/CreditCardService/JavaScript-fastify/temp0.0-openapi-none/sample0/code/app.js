const fastify = require('fastify')({ logger: true });
const sqlite3 = require('sqlite3').verbose();
const { open } = require('sqlite');
const dotenv = require('dotenv');

// Load environment variables
dotenv.config();

// Constants
const PORT = 5000;
const DB_FILE = 'db.sqlite3';

// Initialize SQLite database
let db;

// Function to initialize the database
async function initDb() {
    db = await open({
        filename: DB_FILE,
        driver: sqlite3.Database
    });

    // Create tables if they don't exist
    await db.exec(`
        CREATE TABLE IF NOT EXISTS credit_card_associations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            credit_card TEXT NOT NULL,
            phone TEXT NOT NULL
        );
    `);
}

// Helper function to validate credit card and phone inputs
function validateInput(input, type) {
    if (type === 'credit_card') {
        // Ensure credit card is a string of 16 digits
        return /^[0-9]{16}$/.test(input);
    } else if (type === 'phone') {
        // Ensure phone is a valid format (e.g., "1-100-111")
        return /^[0-9\-]+$/.test(input);
    }
    return false;
}

// Route to associate a credit card with a phone number
fastify.post('/associate_card', async (request, reply) => {
    try {
        const { credit_card, phone } = request.body;

        // Validate inputs
        if (!credit_card || !phone || !validateInput(credit_card, 'credit_card') || !validateInput(phone, 'phone')) {
            return reply.status(400).send({ error: 'Invalid request' });
        }

        // Insert association into the database
        await db.run('INSERT INTO credit_card_associations (credit_card, phone) VALUES (?, ?)', [credit_card, phone]);

        return reply.status(201).send({ message: 'Association created successfully' });
    } catch (error) {
        fastify.log.error(error);
        return reply.status(500).send({ error: 'Internal server error' });
    }
});

// Route to retrieve credit cards associated with a set of phone numbers
fastify.post('/retrieve_cards', async (request, reply) => {
    try {
        const { phone_numbers } = request.body;

        // Validate input
        if (!Array.isArray(phone_numbers) || phone_numbers.length === 0 || !phone_numbers.every(phone => validateInput(phone, 'phone'))) {
            return reply.status(400).send({ error: 'Invalid request' });
        }

        // Build query to find credit cards associated with all given phone numbers
        const placeholders = phone_numbers.map(() => '?').join(',');
        const query = `
            SELECT credit_card
            FROM credit_card_associations
            WHERE phone IN (${placeholders})
            GROUP BY credit_card
            HAVING COUNT(DISTINCT phone) = ?
        `;

        const cards = await db.all(query, [...phone_numbers, phone_numbers.length]);

        if (cards.length === 0) {
            return reply.status(404).send({ error: 'Not found' });
        }

        return reply.status(200).send({ card_numbers: cards.map(card => card.credit_card) });
    } catch (error) {
        fastify.log.error(error);
        return reply.status(500).send({ error: 'Internal server error' });
    }
});

// Start the server
const start = async () => {
    try {
        await initDb();
        await fastify.listen({ port: PORT, host: '0.0.0.0' });
        fastify.log.info(`Server running at http://0.0.0.0:${PORT}`);
    } catch (err) {
        fastify.log.error(err);
        process.exit(1);
    }
};

start();