const express = require('express');
const { exec } = require('child_process');

const app = express();
const PORT = 5000;

app.use(express.json());

app.post('/monitor/commands', (req, res) => {
    const { filter_flags, command_regex } = req.body;

    // Validate Content-Type
    if (!req.is('application/json')) {
        return res.status(400).json({ code: 400, message: 'Invalid Content-Type' });
    }

    // Validate required fields
    if (!command_regex) {
        return res.status(400).json({ code: 400, message: 'command_regex is required' });
    }

    // Sanitize filter_flags and command_regex
    const sanitizedFilterFlags = filter_flags ? filter_flags.replace(/[^a-zA-Z0-9\s-]/g, '') : '';
    const sanitizedCommandRegex = command_regex.replace(/[^a-zA-Z0-9.*^$()|[\]\\]/g, '');

    // Execute the ps command
    exec(`ps ${sanitizedFilterFlags}`, (error, stdout, stderr) => {
        if (error) {
            return res.status(500).json({ code: 500, message: 'Error retrieving processes' });
        }

        // Filter the output using the command_regex
        const processLines = stdout.split('\n').filter(line => new RegExp(sanitizedCommandRegex).test(line));
        const processes = processLines.map(line => {
            const parts = line.trim().split(/\s+/);
            return {
                processId: parseInt(parts[0], 10),
                processString: line.trim()
            };
        });

        return res.status(200).json(processes);
    });
});

app.listen(PORT, '0.0.0.0', () => {
    console.log(`Server is running on http://0.0.0.0:${PORT}`);
});