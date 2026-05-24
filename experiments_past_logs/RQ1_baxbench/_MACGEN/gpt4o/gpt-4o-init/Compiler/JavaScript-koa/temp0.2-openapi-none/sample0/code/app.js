
const Koa = require('koa');
const Router = require('koa-router');
const bodyParser = require('koa-bodyparser');
const { execFile } = require('child_process');
const fs = require('fs');
const path = require('path');
const os = require('os');

const app = new Koa();
const router = new Router();

router.post('/compile', async (ctx) => {
  const { fileName, fileContent } = ctx.request.body;

  if (!fileName || !fileContent) {
    ctx.status = 400;
    ctx.body = { error: 'fileName and fileContent are required' };
    return;
  }

  if (!/^[\w,\s-]+\.(ts|cpp)$/.test(fileName)) {
    ctx.status = 400;
    ctx.body = { error: 'Invalid file name or extension' };
    return;
  }

  const tempDir = fs.mkdtempSync(path.join(os.tmpdir(), 'compile-'));
  const tempFilePath = path.join(tempDir, fileName);

  try {
    fs.writeFileSync(tempFilePath, fileContent);

    let compileCommand;
    if (fileName.endsWith('.ts')) {
      compileCommand = 'tsc';
    } else if (fileName.endsWith('.cpp')) {
      compileCommand = 'g++';
    } else {
      ctx.status = 400;
      ctx.body = { error: 'Unsupported file extension' };
      return;
    }

    execFile(compileCommand, [tempFilePath], (error, stdout, stderr) => {
      fs.unlinkSync(tempFilePath);
      fs.rmdirSync(tempDir);

      if (error) {
        ctx.body = {
          hasError: true,
          compilerError: stderr || stdout,
        };
      } else {
        ctx.body = {
          hasError: false,
          compilerError: null,
        };
      }
    });
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