const Koa = require('koa');
const Router = require('koa-router');
const bodyParser = require('koa-bodyparser');
const { exec } = require('child_process');
const util = require('util');

const app = new Koa();
const router = new Router();
const execPromise = util.promisify(exec);

// Middleware to parse JSON body and validate content-type
app.use(bodyParser({
  enableTypes: ['json'],
  onerror: (err, ctx) => {
    ctx.throw(400, 'Invalid JSON');
  }
}));

// Define the API endpoint
router.post('/monitor/commands', async (ctx) => {
  const { filter_flags, command_regex } = ctx.request.body;

  // Validate input
  if (!command_regex || typeof command_regex !== 'string') {
    ctx.status = 400;
    ctx.body = { code: 400, message: 'Invalid command_regex' };
    return;
  }

  // Sanitize filter_flags to prevent command injection
  const sanitizedFlags = filter_flags ? filter_flags.replace(/[^a-zA-Z0-9\s\-_.]+/g, '') : '';

  try {
    // Execute the ps command safely
    const command = `ps ${sanitizedFlags}`;
    const { stdout } = await execPromise(command);

    // Filter processes based on the command_regex
    const regex = new RegExp(command_regex);
    const processes = stdout.split('\n').slice(1).filter(line => regex.test(line)).map(line => {
      const parts = line.trim().split(/\s+/);
      return {
        processId: parseInt(parts[1], 10),
        processString: line
      };
    });

    ctx.status = 200;
    ctx.body = processes;
  } catch (error) {
    ctx.status = 500;
    ctx.body = { code: 500, message: 'Internal Server Error' };
  }
});

// Error handling
app.on('error', (err, ctx) => {
  console.error('server error', err, ctx);
});

// Use the router
app.use(router.routes()).use(router.allowedMethods());

// Start the server
app.listen(5000, '0.0.0.0', () => {
  console.log('Server running on http://0.0.0.0:5000');
});