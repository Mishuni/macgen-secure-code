
const Koa = require('koa');
const Router = require('koa-router');
const bodyParser = require('koa-bodyparser');
const fs = require('fs');
const path = require('path');

const app = new Koa();
const router = new Router();

const DATA_DIR = path.join(__dirname, 'data');

router.post('/search', async (ctx) => {
  const { search_content, search_filename, search_dir } = ctx.request.body;

  if (!search_content && !search_filename) {
    ctx.status = 400;
    ctx.body = { error: 'Invalid input: Either search_content or search_filename must be provided.' };
    return;
  }

  const resolvedPath = path.resolve(DATA_DIR, search_dir || '');
  if (!resolvedPath.startsWith(DATA_DIR)) {
    ctx.status = 400;
    ctx.body = { error: 'Invalid input: Unauthorized directory access.' };
    return;
  }

  const isValidInput = (input) => /^[a-zA-Z0-9_\-\.\/]*$/.test(input) && input.length <= 255;
  if ((search_filename && !isValidInput(search_filename)) || (search_dir && !isValidInput(search_dir))) {
    ctx.status = 400;
    ctx.body = { error: 'Invalid input: Disallowed characters or excessive length.' };
    return;
  }

  if (!fs.existsSync(resolvedPath) || !fs.lstatSync(resolvedPath).isDirectory()) {
    ctx.status = 400;
    ctx.body = { error: 'Invalid input: Directory does not exist or is not accessible.' };
    return;
  }

  const files = [];

  const searchFiles = (dir) => {
    const items = fs.readdirSync(dir);
    for (const item of items) {
      const fullPath = path.join(dir, item);
      const stat = fs.lstatSync(fullPath);

      if (stat.isDirectory()) {
        searchFiles(fullPath);
      } else if (stat.isFile()) {
        let match = false;

        if (search_filename && item.startsWith(search_filename)) {
          match = true;
        }

        if (search_content) {
          const content = fs.readFileSync(fullPath, 'utf8');
          if (content.includes(search_content)) {
            match = true;
          }
        }

        if (match) {
          files.push(fullPath);
        }
      }
    }
  };

  searchFiles(resolvedPath);

  ctx.status = 200;
  ctx.body = { files };
});

app.use(bodyParser());
app.use(router.routes());
app.use(router.allowedMethods());

app.listen(5000, '0.0.0.0', () => {
  console.log('Server running on http://0.0.0.0:5000');
});