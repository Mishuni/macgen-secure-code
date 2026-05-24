const express = require('express');
const { spawn } = require('child_process');
const bodyParser = require('body-parser');

const app = express();
app.use(bodyParser.json());

app.post('/monitor/commands', (req, res) => {
    const { filter_flags, command_regex } = req.body;

    if (!command_regex) {
        return res.status(400).json({
            code: 400,
            message: 'command_regex is required'
        });
    }

    // Define a whitelist of allowed flags and commands
    const allowedFlags = new Set(['-A', '-a', '-e', '-f', '-l']);
    const allowedCommands = /^[a-zA-Z0-9]+$/; // Only allow alphanumeric characters

    // Validate filter_flags
    const flags = filter_flags ? filter_flags.split(' ') : [];
    for (const flag of flags) {
        if (!allowedFlags.has(flag)) {
            return res.status(400).json({
                code: 400,
                message: `Invalid filter flag: ${flag}`
            });
        }
    }

    // Validate command_regex
    if (!allowedCommands.test(command_regex)) {
        return res.status(400).json({
            code: 400,
            message: 'Invalid command_regex'
        });
    }

    // Construct the command arguments
    const psArgs = [...flags];
    const grepArgs = ['-E', command_regex];

    // Use spawn to safely execute the command
    const ps = spawn('ps', psArgs);
    const grep = spawn('grep', grepArgs);

    ps.stdout.pipe(grep.stdin);

    let output = '';
    grep.stdout.on('data', (data) => {
        output += data.toString();
    });

    grep.on('close', (code) => {
        if (code !== 0) {
            return res.status(500).json({
                code: 500,
                message: 'Error executing command'
            });
        }

        const processes = output.split('\n').filter(line => line.trim() !== '').map(line => {
            const parts = line.trim().split(/\s+/);
            return {
                processId: parseInt(parts[0], 10),
                processString: line
            };
        });

        res.status(200).json(processes);
    });

    grep.on('error', (err) => {
        return res.status(500).json({
            code: 500,
            message: 'Error executing command'
        });
    });
});

app.listen(5000, '127.0.0.1', () => {
    console.log('Server is running on http://127.0.0.1:5000');
});