const Koa = require('koa');
const Router = require('koa-router');
const bodyParser = require('koa-bodyparser');
const { exec } = require('child_process');
const util = require('util');

const execPromise = util.promisify(exec);

const app = new Koa();
const router = new Router();

// Middleware to handle JSON body parsing
app.use(bodyParser());

// Route to handle POST requests to /monitor/commands
router.post('/monitor/commands', async (ctx) => {
    try {
        const { filter_flags, command_regex } = ctx.request.body;

        // Validate input
        if (!command_regex || typeof command_regex !== 'string') {
            ctx.status = 400;
            ctx.body = { code: 400, message: 'Invalid or missing "command_regex" parameter.' };
            return;
        }

        // Sanitize filter_flags to prevent command injection
        const sanitizedFlags = filter_flags && /^[a-zA-Z0-9\s\-]+$/.test(filter_flags) ? filter_flags : '';

        // Construct the ps command
        const psCommand = `ps ${sanitizedFlags} -o pid,command`;

        // Execute the ps command
        const { stdout } = await execPromise(psCommand);

        // Parse the output of the ps command
        const lines = stdout.split('\n').slice(1); // Skip the header line
        const regex = new RegExp(command_regex);
        const processes = lines
            .map((line) => {
                const parts = line.trim().split(/\s+/, 2);
                if (parts.length === 2) {
                    const [pid, command] = parts;
                    return { processId: parseInt(pid, 10), processString: command };
                }
                return null;
            })
            .filter((process) => process && regex.test(process.processString));

        // Respond with the filtered processes
        ctx.status = 200;
        ctx.body = processes;
    } catch (error) {
        console.error('Error processing request:', error);
        ctx.status = 500;
        ctx.body = { code: 500, message: 'Internal server error.' };
    }
});

// Register the router middleware
app.use(router.routes()).use(router.allowedMethods());

// Start the server
const PORT = 5000;
app.listen(PORT, '0.0.0.0', () => {
    console.log(`Server running on http://0.0.0.0:${PORT}`);
});