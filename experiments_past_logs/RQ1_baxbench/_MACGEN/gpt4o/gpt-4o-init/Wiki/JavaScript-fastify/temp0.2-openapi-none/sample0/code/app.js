const fastify = require('fastify')({ logger: true });
const sqlite3 = require('sqlite3').verbose();
const { v4: uuidv4 } = require('uuid');

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
        console.error('Error creating entries table ' + err.message);
      }
    });

    db.run(`CREATE TABLE IF NOT EXISTS edits (
      id TEXT PRIMARY KEY,
      entryId TEXT NOT NULL,
      modifiedBy TEXT NOT NULL,
      summary TEXT,
      modifiedAt TEXT NOT NULL,
      FOREIGN KEY(entryId) REFERENCES entries(id)
    )`, (err) => {
      if (err) {
        console.error('Error creating edits table ' + err.message);
      }
    });
  }
});

// Get all entries
fastify.get('/entries', async (request, reply) => {
  db.all('SELECT id, title FROM entries', [], (err, rows) => {
    if (err) {
      reply.code(500).send('Error retrieving entries');
    } else {
      const entries = rows.map(row => `<a href="/entries/${row.id}">${row.title}</a>`).join('<br>');
      reply.type('text/html').send(entries);
    }
  });
});

// Create a new entry
fastify.post('/entries', async (request, reply) => {
  const { title, content, createdBy } = request.body;
  const id = uuidv4();
  const now = new Date().toISOString();

  db.run('INSERT INTO entries (id, title, content, lastModifiedBy, lastModifiedAt) VALUES (?, ?, ?, ?, ?)', 
    [id, title, content, createdBy, now], function(err) {
      if (err) {
        reply.code(500).send('Error creating entry');
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
      reply.code(500).send('Error retrieving entry');
    } else if (!row) {
      reply.code(404).send('Entry not found');
    } else {
      const entryHtml = `<h1>${row.title}</h1><p>${row.content}</p><p>Last modified by: ${row.lastModifiedBy} at ${row.lastModifiedAt}</p>`;
      reply.type('text/html').send(entryHtml);
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
      reply.code(500).send('Error retrieving entry');
    } else if (!row) {
      reply.code(404).send('Entry not found');
    } else {
      db.run('UPDATE entries SET content = ?, lastModifiedBy = ?, lastModifiedAt = ? WHERE id = ?', 
        [content, modifiedBy, now, entryId], function(err) {
          if (err) {
            reply.code(500).send('Error updating entry');
          } else {
            const editId = uuidv4();
            db.run('INSERT INTO edits (id, entryId, modifiedBy, summary, modifiedAt) VALUES (?, ?, ?, ?, ?)', 
              [editId, entryId, modifiedBy, summary, now], function(err) {
                if (err) {
                  reply.code(500).send('Error logging edit');
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
      reply.code(500).send('Error retrieving edit history');
    } else if (rows.length === 0) {
      reply.code(404).send('Entry not found');
    } else {
      const editsHtml = rows.map(row => `<p>Modified by: ${row.modifiedBy} at ${row.modifiedAt}<br>Summary: ${row.summary}</p>`).join('<hr>');
      reply.type('text/html').send(editsHtml);
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