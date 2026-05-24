const Koa = require('koa');
const Router = require('koa-router');
const bodyParser = require('koa-bodyparser');
const { execFile } = require('child_process');
const fs = require('fs');
const path = require('path');
const util = require('util');

const app = new Koa();
const router = new Router();
const execFilePromise = util.promisify(execFile);

router.post('/compile', async (ctx) => {
  const { fileName, fileContent } = ctx.request.body;

  if (!fileName || !fileContent) {
    ctx.status = 400;
    ctx.body = { error: 'fileName and fileContent are required' };
    return;
  }

  const fileExtension = path.extname(fileName).toLowerCase();
  const safeFileName = path.basename(fileName);
  const tempFilePath = path.join(__dirname, safeFileName);

  if (fileExtension !== '.ts' && fileExtension !== '.cpp') {
    ctx.status = 400;
    ctx.body = { error: 'Unsupported file extension' };
    return;
  }

  try {
    fs.writeFileSync(tempFilePath, fileContent);

    let compileCommand;
    let compileArgs = [];
    if (fileExtension === '.ts') {
      compileCommand = 'tsc';
      compileArgs = [tempFilePath];
    } else if (fileExtension === '.cpp') {
      compileCommand = 'g++';
      compileArgs = [tempFilePath, '-o', `${tempFilePath}.out`];
    }

    try {
      await execFilePromise(compileCommand, compileArgs);
      ctx.body = {
        hasError: false,
        compilerError: null,
      };
    } catch (error) {
      ctx.body = {
        hasError: true,
        compilerError: error.stderr || error.stdout,
      };
    } finally {
      fs.unlinkSync(tempFilePath);
      if (fileExtension === '.cpp') {
        fs.unlinkSync(`${tempFilePath}.out`);
      }
    }
  } catch (err) {
    ctx.status = 500;
    ctx.body = { error: 'Internal server error' };
  }
});

app.use(bodyParser());
app.use(router.routes()).use(router.allowedMethods());

app.listen(5000, '0.0.0.0', () => {
  console.log('Server running on http://0.0.0.0:5000');
});