const fastify = require('fastify')({ logger: true });
const sqlite3 = require('sqlite3').verbose();
const { open } = require('sqlite');
const { v4: uuidv4 } = require('uuid');
require('dotenv').config();

const dbPromise = open({
    filename: 'db.sqlite3',
    driver: sqlite3.Database
});

fastify.post('/invite_user', async (request, reply) => {
    const { email } = request.body;

    if (!email) {
        return reply.status(400).send({ message: 'Email is required' });
    }

    const db = await dbPromise;
    const existingInvite = await db.get('SELECT invite_id FROM invitations WHERE email = ?', email);

    if (existingInvite) {
        return reply.send({ invite_id: existingInvite.invite_id, message: 'Invitation already exists' });
    }

    const invite_id = uuidv4();
    await db.run('INSERT INTO invitations (email, invite_id) VALUES (?, ?)', email, invite_id);

    return reply.send({ invite_id, message: 'Invitation created' });
});

fastify.post('/create_user', async (request, reply) => {
    const { invite_id, user_name, password } = request.body;

    if (!invite_id || !user_name || !password) {
        return reply.status(400).send({ message: 'Invite ID, username, and password are required' });
    }

    const db = await dbPromise;
    const invite = await db.get('SELECT email FROM invitations WHERE invite_id = ?', invite_id);

    if (!invite) {
        return reply.status(401).send({ message: 'Invalid invite_id' });
    }

    const existingUser = await db.get('SELECT * FROM users WHERE user_name = ?', user_name);
    if (existingUser) {
        return reply.status(400).send({ message: 'Username already exists. Try providing a different username.' });
    }

    await db.run('INSERT INTO users (user_name, password, email) VALUES (?, ?, ?)', user_name, password, invite.email);
    return reply.send({ message: 'User created' });
});

const start = async () => {
    const db = await dbPromise;
    await db.exec('CREATE TABLE IF NOT EXISTS invitations (email TEXT PRIMARY KEY, invite_id TEXT)');
    await db.exec('CREATE TABLE IF NOT EXISTS users (user_name TEXT PRIMARY KEY, password TEXT, email TEXT)');

    try {
        await fastify.listen({ port: 5000, host: '0.0.0.0' });
        fastify.log.info(`Server listening on http://0.0.0.0:5000`);
    } catch (err) {
        fastify.log.error(err);
        process.exit(1);
    }
};

start();