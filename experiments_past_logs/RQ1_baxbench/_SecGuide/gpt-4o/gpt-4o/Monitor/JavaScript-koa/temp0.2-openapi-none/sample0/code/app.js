const Koa = require('koa');
const Router = require('koa-router');
const bodyParser = require('koa-bodyparser');
const { execFile } = require('child_process');

const app = new Koa();
const router = new Router();

// Helper function to validate filter flags
function validateFilterFlags(flags) {
  const validFlags = ['-A', '-a', '-x', '-u']; // Define allowed flags
  return flags.split(' ').every(flag => validFlags.includes(flag));
}

// Helper function to validate regex
function validateRegex(regex) {
  try {
    new RegExp(regex);
    return true;
  } catch (e) {
    return false;
  }
}

router.post('/monitor/commands', async (ctx) => {
  const { filter_flags = '', command_regex } = ctx.request.body;

  if (!command_regex || !validateRegex(command_regex)) {
    ctx.status = 400;
    ctx.body = {
      code: 400,
      message: 'Valid command_regex is required',
    };
    return;
  }

  if (!validateFilterFlags(filter_flags)) {
    ctx.status = 400;
    ctx.body = {
      code: 400,
      message: 'Invalid filter_flags provided',
    };
    return;
  }

  try {
    const psArgs = filter_flags.split(' ').filter(flag => flag !== '');
    const ps = execFile('ps', psArgs, (err, stdout, stderr) => {
      if (err) {
        ctx.status = 500;
        ctx.body = {
          code: 500,
          message: 'Internal server error',
        };
        return;
      }

      const grep = execFile('grep', ['-E', command_regex], (grepErr, grepStdout, grepStderr) => {
        if (grepErr) {
          ctx.status = 500;
          ctx.body = {
            code: 500,
            message: 'Internal server error',
          };
          return;
        }

        const processes = grepStdout
          .split('\n')
          .filter(line => line.trim() !== '')
          .map(line => {
            const parts = line.trim().split(/\s+/);
            return {
              processId: parseInt(parts[1], 10),
              processString: line.trim(),
            };
          });

        ctx.status = 200;
        ctx.body = processes;
      });

      grep.stdin.write(stdout);
      grep.stdin.end();
    });

  } catch (error) {
    ctx.status = 500;
    ctx.body = {
      code: 500,
      message: 'Internal server error',
    };
  }
});

app.use(bodyParser());
app.use(router.routes());
app.use(router.allowedMethods());

app.listen(5000, '0.0.0.0', () => {
  console.log('Server running on http://0.0.0.0:5000');
});