const express = require('express');
const { exec } = require('child_process');

const app = express();
const PORT = 5000;

app.use(express.json());

app.post('/monitor/commands', (req, res) => {
    const { filter_flags, command_regex } = req.body;

    if (!command_regex) {
        return res.status(400).json({
            code: 400,
            message: 'command_regex is required'
        });
    }

    // Sanitize filter_flags to prevent command injection
    const sanitizedFlags = filter_flags ? filter_flags.replace(/[^a-zA-Z0-9\s-]/g, '') : '';

    // Construct the ps command
    const psCommand = `ps ${sanitizedFlags} | grep -E '${command_regex}'`;

    exec(psCommand, (error, stdout, stderr) => {
        if (error) {
            return res.status(500).json({
                code: 500,
                message: 'Error executing command'
            });
        }

        const processes = stdout.split('\n')
            .filter(line => line.trim() !== '')
            .map(line => {
                const parts = line.split(/\s+/);
                return {
                    processId: parseInt(parts[0], 10),
                    processString: parts.slice(1).join(' ')
                };
            });

        res.status(200).json(processes);
    });
});

app.listen(PORT, '0.0.0.0', () => {
    console.log(`Server is running on http://0.0.0.0:${PORT}`);
});