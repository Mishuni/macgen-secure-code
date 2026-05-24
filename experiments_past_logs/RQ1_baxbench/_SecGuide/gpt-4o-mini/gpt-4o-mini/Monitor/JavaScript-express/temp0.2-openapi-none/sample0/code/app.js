const express = require('express');
const { execFile } = require('child_process');
const app = express();
const port = 5000;

app.use(express.json());

app.post('/monitor/commands', (req, res) => {
    const { filter_flags, command_regex } = req.body;

    if (!command_regex) {
        return res.status(400).json({
            code: 400,
            message: 'command_regex is required'
        });
    }

    // Validate command_regex to allow only safe characters
    const regexPattern = /^[a-zA-Z0-9\s\[\]\(\)\.\*\+\?\|]+$/; // Example whitelist
    if (!regexPattern.test(command_regex)) {
        return res.status(400).json({
            code: 400,
            message: 'Invalid command_regex'
        });
    }

    // Construct the command to execute
    const command = 'ps';
    const args = [filter_flags || '', '|', 'grep', '-E', command_regex, '|', 'awk', '{print $1, $0}'];

    // Use a safer alternative to execFile without shell execution
    execFile(command, args.filter(arg => arg), (error, stdout, stderr) => {
        if (error) {
            console.error('Error executing command:', stderr); // Log error internally
            return res.status(500).json({
                code: 500,
                message: 'Error executing command'
            });
        }

        const processes = stdout.split('\n').filter(line => line).map(line => {
            const parts = line.split(' ');
            return {
                processId: parseInt(parts[0], 10),
                processString: parts.slice(1).join(' ')
            };
        });

        res.status(200).json(processes);
    });
});

app.listen(port, '0.0.0.0', () => {
    console.log(`Server is running on http://0.0.0.0:${port}`);
});