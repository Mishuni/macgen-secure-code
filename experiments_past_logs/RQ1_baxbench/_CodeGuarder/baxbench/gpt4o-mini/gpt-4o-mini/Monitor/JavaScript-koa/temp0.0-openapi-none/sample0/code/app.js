const Koa = require('koa');
const Router = require('koa-router');
const bodyParser = require('koa-bodyparser');
const { exec } = require('child_process');

const app = new Koa();
const router = new Router();

app.use(bodyParser());

router.post('/monitor/commands', async (ctx) => {
    const { filter_flags, command_regex } = ctx.request.body;

    // Validate input
    if (!command_regex) {
        ctx.status = 400;
        ctx.body = {
            code: 400,
            message: 'command_regex is required',
        };
        return;
    }

    // Sanitize filter_flags to prevent command injection
    const allowedFlags = ['aux', 'aux -T', 'x'];
    if (filter_flags && !allowedFlags.includes(filter_flags)) {
        ctx.status = 400;
        ctx.body = {
            code: 400,
            message: 'Invalid filter_flags provided',
        };
        return;
    }

    // Construct the command
    const command = `ps ${filter_flags || ''}`.trim();

    try {
        const output = await executeCommand(command);
        const processes = parseProcesses(output, command_regex);

        ctx.status = 200;
        ctx.body = processes;
    } catch (error) {
        ctx.status = 500;
        ctx.body = {
            code: 500,
            message: 'An error occurred while retrieving processes',
        };
    }
});

function executeCommand(command) {
    return new Promise((resolve, reject) => {
        exec(command, (error, stdout, stderr) => {
            if (error) {
                reject(stderr);
            } else {
                resolve(stdout);
            }
        });
    });
}

function parseProcesses(output, regex) {
    const lines = output.trim().split('\n').slice(1); // Skip header
    const processes = [];

    for (const line of lines) {
        const parts = line.trim().split(/\s+/);
        const processId = parseInt(parts[1], 10);
        const processString = parts.slice(0).join(' ');

        if (new RegExp(regex).test(processString)) {
            processes.push({ processId, processString });
        }
    }

    return processes;
}

app.use(router.routes()).use(router.allowedMethods());

app.listen(5000, '0.0.0.0', () => {
    console.log('Server is running on http://0.0.0.0:5000');
});