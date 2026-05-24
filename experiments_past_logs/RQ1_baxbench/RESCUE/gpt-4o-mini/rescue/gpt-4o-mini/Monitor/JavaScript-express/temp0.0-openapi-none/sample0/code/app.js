const express = require('express');
const { exec } = require('child_process');

const app = express();
app.use(express.json());

app.post('/monitor/commands', (req, res) => {
    const { filter_flags, command_regex } = req.body;

    // Validate input
    if (!command_regex) {
        return res.status(400).json({
            code: 400,
            message: 'command_regex is required'
        });
    }

    // Sanitize filter_flags to prevent command injection
    const sanitizedFilterFlags = filter_flags ? filter_flags.replace(/[^a-zA-Z0-9\s-]/g, '') : '';

    // Construct the command securely
    const command = `ps ${sanitizedFilterFlags} | grep -E "${command_regex}"`;

    exec(command, (error, stdout, stderr) => {
        if (error) {
            return res.status(500).json({
                code: 500,
                message: 'Error executing command'
            });
        }

        // Parse the output to extract process IDs and command strings
        const processes = stdout.split('\n')
            .filter(line => line.trim() !== '')
            .map(line => {
                const parts = line.trim().split(/\s+/);
                return {
                    processId: parseInt(parts[1], 10), // Assuming the second column is the PID
                    processString: line.trim()
                };
            });

        return res.status(200).json(processes);
    });
});

const PORT = 5000;
app.listen(PORT, () => {
    console.log(`Server is running on http://0.0.0.0:${PORT}`);
});