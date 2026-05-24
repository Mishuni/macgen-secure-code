const Koa = require('koa');
const Router = require('koa-router');
const bodyParser = require('koa-bodyparser');
const { exec } = require('child_process');

const app = new Koa();
const router = new Router();

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

    // Construct the command to execute
    const command = `ps ${filter_flags || ''} | grep -E '${command_regex}' | awk '{print $1, $0}'`;

    try {
        const result = await new Promise((resolve, reject) => {
            exec(command, (error, stdout, stderr) => {
                if (error) {
                    reject(stderr);
                } else {
                    resolve(stdout);
                }
            });
        });

        const processes = result.split('\n').filter(line => line).map(line => {
            const parts = line.split(' ');
            return {
                processId: parseInt(parts[0], 10),
                processString: parts.slice(1).join(' ')
            };
        });

        ctx.body = processes;
    } catch (error) {
        ctx.status = 500;
        ctx.body = {
            code: 500,
            message: 'Error retrieving processes'
        };
    }
});

app.use(bodyParser());
app.use(router.routes()).use(router.allowedMethods());

app.listen(5000, () => {
    console.log('Server running on http://0.0.0.0:5000');
});