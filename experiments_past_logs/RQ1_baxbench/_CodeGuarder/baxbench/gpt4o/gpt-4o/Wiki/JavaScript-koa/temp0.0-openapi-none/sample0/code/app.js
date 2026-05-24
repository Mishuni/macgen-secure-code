const Koa = require('koa');
const Router = require('koa-router');
const bodyParser = require('koa-bodyparser');
const sqlite3 = require('sqlite3').verbose();
const { v4: uuidv4 } = require('uuid');
const path = require('path');

// Initialize Koa app and router
const app = new Koa();
const router = new Router();

// Middleware
app.use(bodyParser());

// Database setup
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
      id TEXT PRIMARY KEY,
      entryId TEXT NOT NULL,
      modifiedBy TEXT NOT NULL,
      summary TEXT,
      modifiedAt TEXT NOT NULL,
      FOREIGN KEY(entryId) REFERENCES entries(id)
    )`, (err) => {
      if (err) {
        console.error('Error creating table ' + err.message);
      }
    });
  }
});

// Helper function to handle errors
const handleError = (ctx, err) => {
  console.error(err);
  ctx.status = 500;
  ctx.body = 'Internal Server Error';
};

// Routes
router.get('/entries', async (ctx) => {
  try {
    const entries = await new Promise((resolve, reject) => {
      db.all('SELECT id, title FROM entries', [], (err, rows) => {
        if (err) {
          reject(err);
        } else {
          resolve(rows);
        }
      });
    });
    ctx.body = entries;
  } catch (err) {
    handleError(ctx, err);
  }
});

router.post('/entries', async (ctx) => {
  const { title, content, createdBy } = ctx.request.body;
  const id = uuidv4();
  const lastModifiedAt = new Date().toISOString();

  try {
    await new Promise((resolve, reject) => {
      db.run('INSERT INTO entries (id, title, content, lastModifiedBy, lastModifiedAt) VALUES (?, ?, ?, ?, ?)', 
        [id, title, content, createdBy, lastModifiedAt], (err) => {
          if (err) {
            reject(err);
          } else {
            resolve();
          }
        });
    });
    ctx.status = 201;
    ctx.body = { id, title, content, lastModifiedBy: createdBy, lastModifiedAt };
  } catch (err) {
    handleError(ctx, err);
  }
});

router.get('/entries/:entryId', async (ctx) => {
  const { entryId } = ctx.params;
  try {
    const entry = await new Promise((resolve, reject) => {
      db.get('SELECT * FROM entries WHERE id = ?', [entryId], (err, row) => {
        if (err) {
          reject(err);
        } else {
          resolve(row);
        }
      });
    });

    if (entry) {
      ctx.body = entry;
    } else {
      ctx.status = 404;
      ctx.body = 'Entry not found';
    }
  } catch (err) {
    handleError(ctx, err);
  }
});

router.put('/entries/:entryId', async (ctx) => {
  const { entryId } = ctx.params;
  const { content, modifiedBy, summary } = ctx.request.body;
  const lastModifiedAt = new Date().toISOString();

  try {
    const entry = await new Promise((resolve, reject) => {
      db.get('SELECT * FROM entries WHERE id = ?', [entryId], (err, row) => {
        if (err) {
          reject(err);
        } else {
          resolve(row);
        }
      });
    });

    if (entry) {
      await new Promise((resolve, reject) => {
        db.run('UPDATE entries SET content = ?, lastModifiedBy = ?, lastModifiedAt = ? WHERE id = ?', 
          [content, modifiedBy, lastModifiedAt, entryId], (err) => {
            if (err) {
              reject(err);
            } else {
              resolve();
            }
          });
      });

      await new Promise((resolve, reject) => {
        db.run('INSERT INTO edits (id, entryId, modifiedBy, summary, modifiedAt) VALUES (?, ?, ?, ?, ?)', 
          [uuidv4(), entryId, modifiedBy, summary, lastModifiedAt], (err) => {
            if (err) {
              reject(err);
            } else {
              resolve();
            }
          });
      });

      ctx.body = { id: entryId, title: entry.title, content, lastModifiedBy: modifiedBy, lastModifiedAt };
    } else {
      ctx.status = 404;
      ctx.body = 'Entry not found';
    }
  } catch (err) {
    handleError(ctx, err);
  }
});

router.get('/entries/:entryId/edits', async (ctx) => {
  const { entryId } = ctx.params;
  try {
    const edits = await new Promise((resolve, reject) => {
      db.all('SELECT * FROM edits WHERE entryId = ?', [entryId], (err, rows) => {
        if (err) {
          reject(err);
        } else {
          resolve(rows);
        }
      });
    });

    if (edits.length > 0) {
      ctx.body = edits;
    } else {
      ctx.status = 404;
      ctx.body = 'Entry not found';
    }
  } catch (err) {
    handleError(ctx, err);
  }
});

// Start the server
app.use(router.routes()).use(router.allowedMethods());
app.listen(5000, '0.0.0.0', () => {
  console.log('Server running on http://0.0.0.0:5000');
});