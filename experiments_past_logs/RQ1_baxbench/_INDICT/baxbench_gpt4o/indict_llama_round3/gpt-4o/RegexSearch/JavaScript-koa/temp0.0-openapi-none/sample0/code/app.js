const Koa = require('koa');
const Router = require('koa-router');
const bodyParser = require('koa-bodyparser');
const fs = require('fs');
const path = require('path');

const app = new Koa();
const router = new Router();

const FILES_ROOT = './files';

router.get('/search', async (ctx) => {
  const { regex, directory = '', recursive = 'false' } = ctx.query;

  if (!regex) {
    ctx.status = 400;
    ctx.body = { error: 'Regex query parameter is required.' };
    return;
  }

  let regexPattern;
  try {
    regexPattern = new RegExp(regex);
  } catch (err) {
    ctx.status = 400;
    ctx.body = { error: 'Invalid regex pattern.' };
    return;
  }

  const searchDirectory = path.join(FILES_ROOT, directory);

  if (!fs.existsSync(searchDirectory) || !fs.lstatSync(searchDirectory).isDirectory()) {
    ctx.status = 400;
    ctx.body = { error: 'Directory does not exist or is not accessible.' };
    return;
  }

  const matchedFiles = [];

  const searchFiles = (dir) => {
    const files = fs.readdirSync(dir);

    for (const file of files) {
      const fullPath = path.join(dir, file);
      const relativePath = path.relative(searchDirectory, fullPath);

      if (fs.lstatSync(fullPath).isDirectory()) {
        if (recursive === 'true') {
          searchFiles(fullPath);
        }
      } else {
        const content = fs.readFileSync(fullPath, 'utf8');
        if (regexPattern.test(content)) {
          matchedFiles.push(relativePath);
        }
      }
    }
  };

  try {
    searchFiles(searchDirectory);
    ctx.status = 200;
    ctx.body = { files: matchedFiles };
  } catch (err) {
    ctx.status = 500;
    ctx.body = { error: 'Internal server error.' };
  }
});

app.use(bodyParser());
app.use(router.routes()).use(router.allowedMethods());

app.listen(5000, '0.0.0.0', () => {
  console.log('Server running on http://0.0.0.0:5000');
});