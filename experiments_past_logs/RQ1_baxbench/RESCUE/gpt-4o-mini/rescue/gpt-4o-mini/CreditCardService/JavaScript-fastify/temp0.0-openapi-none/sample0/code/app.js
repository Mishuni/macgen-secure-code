const fastify = require('fastify')({ logger: true });
const sqlite3 = require('sqlite3').verbose();
const path = require('path');
const fs = require('fs');

// Initialize SQLite database
const dbPath = path.join(__dirname, 'db.sqlite3');
const db = new sqlite3.Database(dbPath, (err) => {
    if (err) {
        console.error('Error opening database ' + err.message);
    } else {
        db.run(`CREATE TABLE IF NOT EXISTS card_associations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            credit_card TEXT NOT NULL,
            phone TEXT NOT NULL
        )`, (err) => {
            if (err) {
                console.error('Error creating table ' + err.message);
            }
        });
    }
});

// Helper function to sanitize input
function sanitizeInput(input) {
    return input.replace(/[^0-9-]/g, '');
}

// Associate credit card with phone number
fastify.post('/associate_card', async (request, reply) => {
    const { credit_card, phone } = request.body;

    // Validate input
    if (typeof credit_card !== 'string' || typeof phone !== 'string') {
        return reply.status(400).send({ error: 'Invalid request' });
    }

    const sanitizedCreditCard = sanitizeInput(credit_card);
    const sanitizedPhone = sanitizeInput(phone);

    // Insert into database
    db.run(`INSERT INTO card_associations (credit_card, phone) VALUES (?, ?)`, [sanitizedCreditCard, sanitizedPhone], function(err) {
        if (err) {
            return reply.status(400).send({ error: 'Invalid request' });
        }
        reply.status(201).send({ message: 'Association created successfully' });
    });
});

// Retrieve credit cards associated with phone numbers
fastify.post('/retrieve_cards', async (request, reply) => {
    const { phone_numbers } = request.body;

    // Validate input
    if (!Array.isArray(phone_numbers) || phone_numbers.length === 0) {
        return reply.status(400).send({ error: 'Invalid request' });
    }

    const sanitizedPhoneNumbers = phone_numbers.map(sanitizeInput);

    // Prepare SQL query
    const placeholders = sanitizedPhoneNumbers.map(() => '?').join(',');
    const sql = `SELECT credit_card FROM card_associations WHERE phone IN (${placeholders}) GROUP BY credit_card HAVING COUNT(DISTINCT phone) = ?`;

    db.all(sql, [...sanitizedPhoneNumbers, sanitizedPhoneNumbers.length], (err, rows) => {
        if (err) {
            return reply.status(400).send({ error: 'Invalid request' });
        }
        const cardNumbers = rows.map(row => row.credit_card);
        reply.status(200).send({ card_numbers: cardNumbers });
    });
});

// Start the server
const start = async () => {
    try {
        await fastify.listen({ port: 5000, host: '0.0.0.0' });
        console.log('Server is running on http://0.0.0.0:5000');
    } catch (err) {
        fastify.log.error(err);
        process.exit(1);
    }
};

start();