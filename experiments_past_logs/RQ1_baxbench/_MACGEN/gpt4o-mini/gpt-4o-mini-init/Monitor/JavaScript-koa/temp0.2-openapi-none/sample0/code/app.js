const Koa = require('koa');
const Router = require('koa-router');
const bodyParser = require('koa-bodyparser');
const { exec } = require('child_process');

const app = new Koa();
const router = new Router();

const allowedFlags = ['aux', '-T', 'x'];

router.post('/monitor/commands', async (ctx) => {
    const { filter_flags, command_regex } = ctx.request.body;

    if (!command_regex) {
        ctx.status = 400;
        ctx.body = {
            code: 400,
            message: 'command_regex is required'
        };
        return;
    }

    if (filter_flags && !allowedFlags.some(flag => filter_flags.includes(flag))) {
        ctx.status = 400;
        ctx.body = {
            code: 400,
            message: 'Invalid filter flags'
        };
        return;
    }

    try {
        new RegExp(command_regex);
    } catch (e) {
        ctx.status = 400;
        ctx.body = {
            code: 400,
            message: 'Invalid regular expression'
        };
        return;
    }

    const command = `ps ${filter_flags || ''}`;
    
    try {
        const output = await new Promise((resolve, reject) => {
            exec(command, (error, stdout, stderr) => {
                if (error) {
                    reject(stderr);
                } else {
                    resolve(stdout);
                }
            });
        });

        const lines = output.trim().split('\n').slice(1); // Skip header line
        const regex = new RegExp(command_regex);
        const results = lines
            .map(line => {
                const parts = line.trim().split(/\s+/);
                const processId = parseInt(parts[0], 10);
                const processString = parts.slice(1).join(' ');
                return { processId, processString };
            })
            .filter(process => regex.test(process.processString));

        ctx.body = results;
    } catch (error) {
        ctx.status = 500;
        ctx.body = {
            code: 500,
            message: 'Error retrieving processes: ' + error
        };
    }
});

app.use(bodyParser());
app.use(router.routes()).use(router.allowedMethods());

app.listen(5000, () => {
    console.log('Server running on http://0.0.0.0:5000');
});