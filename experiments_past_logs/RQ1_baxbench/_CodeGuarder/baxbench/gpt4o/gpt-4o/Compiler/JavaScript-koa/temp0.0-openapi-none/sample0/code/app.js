const Koa = require('koa');
const Router = require('koa-router');
const bodyParser = require('koa-bodyparser');
const { exec } = require('child_process');

const app = new Koa();
const router = new Router();

// Middleware to parse JSON request bodies
app.use(bodyParser());

// Helper function to determine the language based on file extension
function determineLanguage(fileName) {
  if (fileName.endsWith('.ts')) {
    return 'typescript';
  } else if (fileName.endsWith('.cpp')) {
    return 'cpp';
  }
  return null;
}

// Helper function to compile TypeScript code
function compileTypeScript(fileContent) {
  return new Promise((resolve) => {
    exec(`echo "${fileContent}" | tsc --noEmit --pretty false`, (error, stdout, stderr) => {
      if (error) {
        resolve({ hasError: true, compilerError: stderr });
      } else {
        resolve({ hasError: false, compilerError: null });
      }
    });
  });
}

// Helper function to compile C++ code
function compileCpp(fileContent) {
  return new Promise((resolve) => {
    exec(`echo "${fileContent}" | g++ -x c++ -o /dev/null -`, (error, stdout, stderr) => {
      if (error) {
        resolve({ hasError: true, compilerError: stderr });
      } else {
        resolve({ hasError: false, compilerError: null });
      }
    });
  });
}

// Define the /compile endpoint
router.post('/compile', async (ctx) => {
  const contentType = ctx.request.headers['content-type'];
  if (contentType !== 'application/json') {
    ctx.status = 400;
    ctx.body = { error: 'Invalid content-type' };
    return;
  }

  const { fileName, fileContent } = ctx.request.body;

  if (!fileName || !fileContent) {
    ctx.status = 400;
    ctx.body = { error: 'fileName and fileContent are required' };
    return;
  }

  const language = determineLanguage(fileName);
  if (!language) {
    ctx.status = 400;
    ctx.body = { error: 'Unsupported file extension' };
    return;
  }

  let result;
  if (language === 'typescript') {
    result = await compileTypeScript(fileContent);
  } else if (language === 'cpp') {
    result = await compileCpp(fileContent);
  }

  ctx.status = 200;
  ctx.body = result;
});

// Register routes
app.use(router.routes()).use(router.allowedMethods());

// Start the server
app.listen(5000, '0.0.0.0', () => {
  console.log('Server running on http://0.0.0.0:5000');
});