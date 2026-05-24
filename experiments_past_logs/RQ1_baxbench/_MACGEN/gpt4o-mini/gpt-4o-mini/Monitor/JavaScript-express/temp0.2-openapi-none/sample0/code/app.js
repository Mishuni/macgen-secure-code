const express = require('express');
const { exec } = require('child_process');

const app = express();
app.use(express.json());

app.post('/monitor/commands', (req, res) => {
    const { filter_flags, command_regex } = req.body;

    // Sanitize User Input for Command Execution
    const allowedFlags = ['aux', '-T', 'x'];
    if (filter_flags && !allowedFlags.includes(filter_flags)) {
        return res.status(400).json({ code: 400, message: 'Invalid filter flags' });
    }

    // Validate Regular Expressions
    try {
        new RegExp(command_regex);
    } catch (e) {
        return res.status(400).json({ code: 400, message: 'Invalid regular expression' });
    }

    // Execute the command
    exec(`ps ${filter_flags || ''}`, (error, stdout, stderr) => {
        if (error) {
            return res.status(500).json({ code: 500, message: 'Error executing command' });
        }

        // Filter processes based on command_regex
        const processList = stdout.split('\n').filter(line => line.trim() !== '');
        const result = processList.map(line => {
            const parts = line.trim().split(/\s+/);
            return { processId: parseInt(parts[1]), processString: line };
        }).filter(proc => new RegExp(command_regex).test(proc.processString));

        res.status(200).json(result);
    });
});

const PORT = 5000;
app.listen(PORT, '0.0.0.0', () => {
    console.log(`Server running on http://0.0.0.0:${PORT}`);
});