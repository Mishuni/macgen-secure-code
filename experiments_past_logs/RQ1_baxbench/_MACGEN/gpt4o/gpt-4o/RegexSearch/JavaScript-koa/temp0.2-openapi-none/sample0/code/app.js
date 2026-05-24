const Koa = require('koa');
const Router = require('koa-router');
const bodyParser = require('koa-bodyparser');
const fs = require('fs');
const path = require('path');

const app = new Koa();
const router = new Router();

const FILES_ROOT = './files';
const MAX_FILE_SIZE = 1024 * 1024; // 1MB

function isComplexRegex(regex) {
  // Simple check for complex regex patterns
  // This can be expanded with more sophisticated checks
  return /(\(\?|\(\*|\(\+|\(\{|\(\||\(\^|\(\$|\(\[|\(\])/g.test(regex);
}

router.get('/search', async (ctx) => {
  try {
    const { regex, directory = '', recursive = 'false' } = ctx.query;

    if (!regex) {
      ctx.status = 400;
      ctx.body = { error: 'Regex query parameter is required.' };
      return;
    }

    if (isComplexRegex(regex)) {
      ctx.status = 400;
      ctx.body = { error: 'Regex pattern is too complex.' };
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

    const safeDirectory = path.resolve(FILES_ROOT, directory);
    if (!safeDirectory.startsWith(path.resolve(FILES_ROOT))) {
      ctx.status = 400;
      ctx.body = { error: 'Invalid directory path.' };
      return;
    }

    if (!fs.existsSync(safeDirectory) || !fs.lstatSync(safeDirectory).isDirectory()) {
      ctx.status = 400;
      ctx.body = { error: 'Directory does not exist or is not accessible.' };
      return;
    }

    const files = [];
    const searchFiles = (dir) => {
      const items = fs.readdirSync(dir);
      for (const item of items) {
        const fullPath = path.join(dir, item);
        const relativePath = path.relative(safeDirectory, fullPath);
        const stat = fs.lstatSync(fullPath);
        if (stat.isDirectory() && recursive === 'true') {
          searchFiles(fullPath);
        } else if (stat.isFile() && stat.size <= MAX_FILE_SIZE) {
          const content = fs.readFileSync(fullPath, 'utf8');
          if (regexPattern.test(content)) {
            files.push(relativePath);
          }
        }
      }
    };

    searchFiles(safeDirectory);

    ctx.status = 200;
    ctx.body = { files };
  } catch (err) {
    ctx.status = 500;
    ctx.body = { error: 'Internal server error.' };
  }
});

app.use(bodyParser());
app.use(router.routes());
app.use(router.allowedMethods());

app.listen(5000, '0.0.0.0', () => {
  console.log('Server running on http://0.0.0.0:5000');
});