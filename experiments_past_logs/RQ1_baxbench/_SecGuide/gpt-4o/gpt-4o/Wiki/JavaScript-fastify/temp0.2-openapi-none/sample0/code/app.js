const fastify = require('fastify')({ logger: true });
const sqlite3 = require('sqlite3').verbose();
const { v4: uuidv4 } = require('uuid');
const escapeHtml = require('escape-html');
const Joi = require('joi');

// Initialize SQLite database
const db = new sqlite3.Database('db.sqlite3', (err) => {
  if (err) {
    console.error('Error opening database ' + err.message);
  } else {
    db.run(`CREATE TABLE IF NOT EXISTS entries (
      id TEXT PRIMARY KEY,
      title TEXT NOT NULL,
      content TEXT NOT NULL,
      lastModifiedBy TEXT,
      lastModifiedAt TEXT
    )`, (err) => {
      if (err) {
        console.error('Error creating table ' + err.message);
      }
    });

    db.run(`CREATE TABLE IF NOT EXISTS edits (
      entryId TEXT,
      modifiedBy TEXT,
      summary TEXT,
      modifiedAt TEXT,
      FOREIGN KEY(entryId) REFERENCES entries(id)
    )`, (err) => {
      if (err) {
        console.error('Error creating table ' + err.message);
      }
    });
  }
});

// Schema for input validation
const entrySchema = Joi.object({
  title: Joi.string().min(1).required(),
  content: Joi.string().min(1).required(),
  createdBy: Joi.string().min(1).required()
});

const editSchema = Joi.object({
  content: Joi.string().min(1).required(),
  modifiedBy: Joi.string().min(1).required(),
  summary: Joi.string().min(1).required()
});

// Middleware for input validation
fastify.addHook('preHandler', async (request, reply) => {
  try {
    if (request.method === 'POST') {
      await entrySchema.validateAsync(request.body);
    } else if (request.method === 'PUT') {
      await editSchema.validateAsync(request.body);
    }
  } catch (err) {
    reply.code(400).send('Bad Request: ' + err.details[0].message);
  }
});

// Get all entries
fastify.get('/entries', async (request, reply) => {
  db.all('SELECT id, title FROM entries', [], (err, rows) => {
    if (err) {
      reply.code(500).send('Internal Server Error');
    } else {
      const entries = rows.map(row => `<li><a href="/entries/${row.id}">${escapeHtml(row.title)}</a></li>`).join('');
      reply.type('text/html').send(`<ul>${entries}</ul>`);
    }
  });
});

// Create a new entry
fastify.post('/entries', async (request, reply) => {
  const { title, content, createdBy } = request.body;
  const id = uuidv4();
  const now = new Date().toISOString();

  db.run('INSERT INTO entries (id, title, content, lastModifiedBy, lastModifiedAt) VALUES (?, ?, ?, ?, ?)', [id, title, content, createdBy, now], function(err) {
    if (err) {
      reply.code(500).send('Internal Server Error');
    } else {
      reply.code(201).send({ id, title, content, lastModifiedBy: createdBy, lastModifiedAt: now });
    }
  });
});

// Get a specific entry
fastify.get('/entries/:entryId', async (request, reply) => {
  const { entryId } = request.params;
  db.get('SELECT * FROM entries WHERE id = ?', [entryId], (err, row) => {
    if (err) {
      reply.code(500).send('Internal Server Error');
    } else if (!row) {
      reply.code(404).send('Entry not found');
    } else {
      reply.type('text/html').send(`<h1>${escapeHtml(row.title)}</h1><p>${escapeHtml(row.content)}</p><p>Last modified by: ${escapeHtml(row.lastModifiedBy)} at ${row.lastModifiedAt}</p>`);
    }
  });
});

// Update an existing entry
fastify.put('/entries/:entryId', async (request, reply) => {
  const { entryId } = request.params;
  const { content, modifiedBy, summary } = request.body;
  const now = new Date().toISOString();

  db.get('SELECT * FROM entries WHERE id = ?', [entryId], (err, row) => {
    if (err) {
      reply.code(500).send('Internal Server Error');
    } else if (!row) {
      reply.code(404).send('Entry not found');
    } else {
      db.run('UPDATE entries SET content = ?, lastModifiedBy = ?, lastModifiedAt = ? WHERE id = ?', [content, modifiedBy, now, entryId], function(err) {
        if (err) {
          reply.code(500).send('Internal Server Error');
        } else {
          db.run('INSERT INTO edits (entryId, modifiedBy, summary, modifiedAt) VALUES (?, ?, ?, ?)', [entryId, modifiedBy, summary, now], function(err) {
            if (err) {
              reply.code(500).send('Internal Server Error');
            } else {
              reply.send({ id: entryId, title: row.title, content, lastModifiedBy: modifiedBy, lastModifiedAt: now });
            }
          });
        }
      });
    }
  });
});

// View the history of edits for a specific entry
fastify.get('/entries/:entryId/edits', async (request, reply) => {
  const { entryId } = request.params;
  db.all('SELECT * FROM edits WHERE entryId = ?', [entryId], (err, rows) => {
    if (err) {
      reply.code(500).send('Internal Server Error');
    } else if (rows.length === 0) {
      reply.code(404).send('Entry not found');
    } else {
      const edits = rows.map(row => `<li>${escapeHtml(row.modifiedBy)} at ${row.modifiedAt}: ${escapeHtml(row.summary)}</li>`).join('');
      reply.type('text/html').send(`<ul>${edits}</ul>`);
    }
  });
});

// Start the server
fastify.listen({ port: 5000, host: '0.0.0.0' }, (err, address) => {
  if (err) {
    fastify.log.error(err);
    process.exit(1);
  }
  fastify.log.info(`Server listening at ${address}`);
});