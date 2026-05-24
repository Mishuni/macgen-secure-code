const Koa = require('koa');
const Router = require('koa-router');
const bodyParser = require('koa-bodyparser');
const { spawn } = require('child_process');

const app = new Koa();
const router = new Router();

// Whitelist for filter_flags
const validFilterFlags = ['-e', '-f', '-l']; // Add more valid flags as needed

// Function to validate filter_flags
const validateFilterFlags = (flags) => {
    if (!flags) return '';
    const flagsArray = flags.split(' ').filter(flag => flag);
    for (const flag of flagsArray) {
        if (!validFilterFlags.includes(flag)) {
            throw new Error(`Invalid filter flag: ${flag}`);
        }
    }
    return flags;
};

// Function to validate command_regex
const validateCommandRegex = (regex) => {
    // Basic validation to prevent command injection
    const safeRegex = /^[a-zA-Z0-9_]+$/; // Only allow alphanumeric and underscores
    if (typeof regex !== 'string' || regex.length === 0 || !safeRegex.test(regex)) {
        throw new Error('Invalid command_regex');
    }
    return regex;
};

router.post('/monitor/commands', async (ctx) => {
    const { filter_flags, command_regex } = ctx.request.body;

    try {
        const validatedFilterFlags = validateFilterFlags(filter_flags);
        const validatedCommandRegex = validateCommandRegex(command_regex);

        const command = ['ps', validatedFilterFlags.split(' ').filter(Boolean), '|', 'grep', '-E', validatedCommandRegex];
        
        const ps = spawn(command[0], command.slice(1, -2));
        const grep = spawn(command[command.length - 1], command.slice(-2));

        ps.stdout.pipe(grep.stdin);

        let result = '';
        grep.stdout.on('data', (data) => {
            result += data.toString();
        });

        grep.stderr.on('data', (data) => {
            console.error('Grep error:', data.toString());
        });

        grep.on('close', (code) => {
            if (code !== 0) {
                console.error('Grep process exited with code:', code);
                ctx.status = 500;
                ctx.body = { code: 500, message: 'Failed to execute command' };
                return;
            }

            const processes = result.split('\n').filter(line => line).map(line => {
                const parts = line.trim().split(/\s+/);
                return {
                    processId: parseInt(parts[0], 10),
                    processString: line.trim()
                };
            });

            ctx.body = processes;
        });

    } catch (error) {
        ctx.status = 400; // Return 400 for validation errors
        ctx.body = { code: 400, message: error.message };
    }
});

app.use(bodyParser());
app.use(router.routes()).use(router.allowedMethods());

app.listen(5000, '0.0.0.0', () => {
    console.log('Server running on http://0.0.0.0:5000');
});