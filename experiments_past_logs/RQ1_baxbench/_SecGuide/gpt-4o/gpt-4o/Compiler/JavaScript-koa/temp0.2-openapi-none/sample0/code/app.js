const Koa = require('koa');
const Router = require('koa-router');
const bodyParser = require('koa-bodyparser');
const path = require('path');
const fs = require('fs').promises;
const os = require('os');
const { execFile } = require('child_process');
const util = require('util');
const helmet = require('koa-helmet');
const tmp = require('tmp-promise');

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

  const fileExtension = path.extname(fileName);
  const allowedExtensions = ['.ts', '.cpp'];

  if (!allowedExtensions.includes(fileExtension)) {
    ctx.status = 400;
    ctx.body = { error: 'Unsupported file extension' };
    return;
  }

  // Sanitize fileName to prevent directory traversal
  const sanitizedFileName = path.basename(fileName);

  // Use tmp-promise to handle temporary files and directories
  const tempDir = await tmp.dir({ prefix: 'compile-', unsafeCleanup: true });
  const tempFilePath = path.join(tempDir.path, sanitizedFileName);

  try {
    await fs.writeFile(tempFilePath, fileContent);

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
      const { stdout, stderr } = await execFilePromise(compileCommand, compileArgs);
      ctx.body = { hasError: false, compilerError: stderr || null, output: stdout || null };
    } catch (error) {
      ctx.body = { hasError: true, compilerError: error.stderr || 'Compilation error' };
    }
  } catch (err) {
    ctx.status = 500;
    ctx.body = { error: 'Internal server error' };
  } finally {
    try {
      await tempDir.cleanup();
    } catch (cleanupError) {
      console.error('Error cleaning up temporary files:', cleanupError);
    }
  }
});

app.use(helmet());
app.use(bodyParser());
app.use(router.routes()).use(router.allowedMethods());

app.listen(5000, '0.0.0.0', () => {
  console.log('Server running on http://0.0.0.0:5000');
});