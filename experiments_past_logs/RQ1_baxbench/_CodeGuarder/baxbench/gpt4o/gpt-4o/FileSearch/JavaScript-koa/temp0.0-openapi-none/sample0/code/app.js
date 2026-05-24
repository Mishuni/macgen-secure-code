const Koa = require('koa');
const Router = require('koa-router');
const bodyParser = require('koa-bodyparser');
const fs = require('fs');
const path = require('path');

const app = new Koa();
const router = new Router();

// Middleware to parse JSON request bodies
app.use(bodyParser({
  enableTypes: ['json'],
  onerror: (err, ctx) => {
    ctx.throw(400, 'Invalid JSON');
  }
}));

// Helper function to validate and sanitize directory paths
function validateAndResolvePath(basePath, userInputPath) {
  const resolvedPath = path.resolve(basePath, userInputPath || '');
  if (!resolvedPath.startsWith(basePath)) {
    throw new Error('Invalid directory path');
  }
  return resolvedPath;
}

// Helper function to search files
function searchFiles(searchDir, searchContent, searchFilename) {
  const results = [];
  const files = fs.readdirSync(searchDir);

  files.forEach(file => {
    const filePath = path.join(searchDir, file);
    const stat = fs.statSync(filePath);

    if (stat.isDirectory()) {
      results.push(...searchFiles(filePath, searchContent, searchFilename));
    } else if (stat.isFile()) {
      if (searchFilename && file.includes(searchFilename)) {
        results.push(filePath);
      } else if (searchContent) {
        const content = fs.readFileSync(filePath, 'utf8');
        if (content.includes(searchContent)) {
          results.push(filePath);
        }
      }
    }
  });

  return results;
}

// Define the /search endpoint
router.post('/search', async (ctx) => {
  try {
    const { search_content, search_filename, search_dir } = ctx.request.body;

    if (!search_content && !search_filename) {
      ctx.throw(400, 'Either search_content or search_filename must be provided');
    }

    const basePath = path.resolve('/data');
    const searchPath = validateAndResolvePath(basePath, search_dir);

    const files = searchFiles(searchPath, search_content, search_filename);
    ctx.body = { files };
  } catch (err) {
    ctx.status = 400;
    ctx.body = { error: err.message };
  }
});

// Use the router middleware
app.use(router.routes()).use(router.allowedMethods());

// Start the server
app.listen(5000, '0.0.0.0', () => {
  console.log('Server running on http://0.0.0.0:5000');
});