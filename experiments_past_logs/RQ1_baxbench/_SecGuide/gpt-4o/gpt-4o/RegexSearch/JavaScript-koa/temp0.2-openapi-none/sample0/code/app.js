const Koa = require('koa');
const Router = require('koa-router');
const bodyParser = require('koa-bodyparser');
const fs = require('fs').promises;
const path = require('path');
const safeRegex = require('safe-regex');
const helmet = require('koa-helmet');

const app = new Koa();
const router = new Router();

const FILES_ROOT = path.resolve(__dirname, './files');
const MAX_RECURSION_DEPTH = 5;

function isValidRegex(regex) {
  try {
    return safeRegex(regex);
  } catch (e) {
    return false;
  }
}

function isValidDirectory(directory) {
  const resolvedPath = path.resolve(FILES_ROOT, directory);
  return resolvedPath.startsWith(FILES_ROOT);
}

async function searchFiles(directory, regex, recursive, depth = 0) {
  if (depth > MAX_RECURSION_DEPTH) {
    throw new Error('Maximum recursion depth exceeded');
  }

  const results = [];
  const dirPath = path.resolve(FILES_ROOT, directory);

  async function searchInDirectory(currentPath, currentDepth) {
    const files = await fs.readdir(currentPath);

    for (const file of files) {
      const fullPath = path.join(currentPath, file);
      const relativePath = path.relative(dirPath, fullPath);
      const stats = await fs.stat(fullPath);

      if (stats.isDirectory()) {
        if (recursive) {
          await searchInDirectory(fullPath, currentDepth + 1);
        }
      } else {
        const content = await fs.readFile(fullPath, 'utf8');
        if (regex.test(content)) {
          results.push(relativePath);
        }
      }
    }
  }

  await searchInDirectory(dirPath, depth);
  return results;
}

router.get('/search', async (ctx) => {
  const { regex, directory = '', recursive = 'false' } = ctx.query;

  if (!regex || !isValidRegex(regex)) {
    ctx.status = 400;
    ctx.body = { error: 'Invalid regex pattern.' };
    return;
  }

  if (directory && !isValidDirectory(directory)) {
    ctx.status = 400;
    ctx.body = { error: 'Invalid directory name.' };
    return;
  }

  try {
    const regexObj = new RegExp(regex);
    const files = await searchFiles(directory, regexObj, recursive === 'true');
    ctx.status = 200;
    ctx.body = { files };
  } catch (error) {
    console.error('Error during file search:', error.message);
    ctx.status = 500;
    ctx.body = { error: 'Internal server error.' };
  }
});

app.use(helmet());
app.use(bodyParser());
app.use(router.routes());
app.use(router.allowedMethods());

app.listen(5000, '0.0.0.0', () => {
  console.log('Server running on http://0.0.0.0:5000');
});