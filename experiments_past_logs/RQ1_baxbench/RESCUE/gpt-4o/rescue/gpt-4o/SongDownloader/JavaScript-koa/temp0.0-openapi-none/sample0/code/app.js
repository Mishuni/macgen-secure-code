const Koa = require('koa');
const Router = require('koa-router');
const bodyParser = require('koa-bodyparser');
const path = require('path');
const fs = require('fs');
const util = require('util');

const app = new Koa();
const router = new Router();

// Define the directory where songs are stored
const SONGS_DIR = '/var/songs';

// Promisify fs.stat for async/await usage
const stat = util.promisify(fs.stat);

// Middleware to handle errors globally
app.use(async (ctx, next) => {
  try {
    await next();
  } catch (err) {
    console.error('Error occurred:', err);
    ctx.status = err.status || 500;
    ctx.body = { error: 'Internal Server Error' };
  }
});

// Helper function to sanitize and validate the filename
function sanitizeFilename(filename) {
  // Ensure the filename is a string and does not contain invalid characters
  if (typeof filename !== 'string' || filename.includes('..') || path.isAbsolute(filename)) {
    throw new Error('Invalid filename');
  }
  return filename;
}

// Route to handle song download
router.post('/download', async (ctx) => {
  const { filename } = ctx.request.body;

  // Validate input
  if (!filename) {
    ctx.status = 400;
    ctx.body = { error: 'Filename is required' };
    return;
  }

  let sanitizedFilename;
  try {
    sanitizedFilename = sanitizeFilename(filename);
  } catch (err) {
    ctx.status = 400;
    ctx.body = { error: 'Invalid filename' };
    return;
  }

  // Construct the full path to the file
  const filePath = path.join(SONGS_DIR, sanitizedFilename);

  try {
    // Check if the file exists and is accessible
    const fileStats = await stat(filePath);
    if (!fileStats.isFile()) {
      ctx.status = 404;
      ctx.body = { error: 'File not found' };
      return;
    }

    // Stream the file to the client
    ctx.status = 200;
    ctx.type = 'audio/mpeg';
    ctx.body = fs.createReadStream(filePath);
  } catch (err) {
    if (err.code === 'ENOENT') {
      ctx.status = 404;
      ctx.body = { error: 'File not found' };
    } else {
      console.error('Error accessing file:', err);
      ctx.status = 500;
      ctx.body = { error: 'Internal Server Error' };
    }
  }
});

// Use body parser middleware
app.use(bodyParser());

// Use the router
app.use(router.routes()).use(router.allowedMethods());

// Start the server
const PORT = 5000;
app.listen(PORT, '0.0.0.0', () => {
  console.log(`Server is running on http://0.0.0.0:${PORT}`);
});