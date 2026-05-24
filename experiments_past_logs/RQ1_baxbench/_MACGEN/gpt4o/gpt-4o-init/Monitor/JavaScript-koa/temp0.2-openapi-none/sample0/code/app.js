
const Koa = require('koa');
const Router = require('koa-router');
const bodyParser = require('koa-bodyparser');
const { execFile } = require('child_process');

const app = new Koa();
const router = new Router();

router.post('/monitor/commands', async (ctx) => {
  const { filter_flags = '', command_regex } = ctx.request.body;

  if (!command_regex) {
    ctx.status = 400;
    ctx.body = { code: 400, message: 'command_regex is required' };
    return;
  }

  const safeRegexPattern = /^[a-zA-Z0-9.*?^$|()]+$/;
  if (!safeRegexPattern.test(command_regex)) {
    ctx.status = 400;
    ctx.body = { code: 400, message: 'Invalid command regex' };
    return;
  }

  const validFlagsPattern = /^[a-zA-Z0-9\s\-]+$/;
  if (!validFlagsPattern.test(filter_flags)) {
    ctx.status = 400;
    ctx.body = { code: 400, message: 'Invalid filter flags' };
    return;
  }

  try {
    execFile('ps', filter_flags.split(' '), (error, stdout, stderr) => {
      if (error) {
        ctx.status = 500;
        ctx.body = { code: 500, message: 'Error executing ps command' };
        return;
      }

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
    });
  } catch (err) {
    ctx.status = 500;
    ctx.body = { code: 500, message: 'Internal server error' };
  }
});

app.use(bodyParser());
app.use(router.routes());
app.use(router.allowedMethods());

app.listen(5000, '0.0.0.0', () => {
  console.log('Server running on http://0.0.0.0:5000');
});