const Koa = require('koa');
const Router = require('koa-router');
const bodyParser = require('koa-bodyparser');
const { exec } = require('child_process');

const app = new Koa();
const router = new Router();

router.post('/monitor/commands', async (ctx) => {
  const { filter_flags = '', command_regex } = ctx.request.body;

  if (!command_regex) {
    ctx.status = 400;
    ctx.body = {
      code: 400,
      message: 'command_regex is required',
    };
    return;
  }

  // Validate and sanitize filter_flags to prevent command injection
  const validFlags = /^[a-zA-Z\s\-]*$/;
  if (!validFlags.test(filter_flags)) {
    ctx.status = 400;
    ctx.body = {
      code: 400,
      message: 'Invalid filter_flags',
    };
    return;
  }

  try {
    const command = `ps ${filter_flags}`;
    const processes = await new Promise((resolve, reject) => {
      exec(command, (error, stdout, stderr) => {
        if (error) {
          reject(stderr);
        } else {
          resolve(stdout);
        }
      });
    });

    const regex = new RegExp(command_regex);
    const processList = processes.split('\n').slice(1).filter(line => regex.test(line)).map(line => {
      const parts = line.trim().split(/\s+/);
      const pidIndex = filter_flags.includes('aux') ? 1 : 0; // Adjust index based on flags
      return {
        processId: parseInt(parts[pidIndex], 10),
        processString: line,
      };
    });

    ctx.status = 200;
    ctx.body = processList;
  } catch (error) {
    ctx.status = 500;
    ctx.body = {
      code: 500,
      message: 'Internal Server Error',
    };
  }
});

app
  .use(bodyParser())
  .use(router.routes())
  .use(router.allowedMethods());

app.listen(5000, '0.0.0.0', () => {
  console.log('Server running on http://0.0.0.0:5000');
});