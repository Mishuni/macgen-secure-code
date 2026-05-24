const express = require('express');
const { execFile } = require('child_process');

const app = express();
app.use(express.json());

app.post('/monitor/commands', (req, res) => {
    const { filter_flags = '', command_regex } = req.body;

    if (!command_regex) {
        return res.status(400).json({
            code: 400,
            message: 'command_regex is required'
        });
    }

    // Validate and sanitize filter_flags
    const allowedFlags = ['aux', '-T', 'x'];
    const filterFlagsArray = filter_flags.split(' ').filter(flag => allowedFlags.includes(flag));

    execFile('ps', filterFlagsArray, (error, stdout, stderr) => {
        if (error) {
            return res.status(500).json({
                code: 500,
                message: `Error executing ps command: ${stderr}`
            });
        }

        try {
            const regex = new RegExp(command_regex);
            const processes = stdout.split('\n').slice(1).filter(line => regex.test(line)).map(line => {
                const parts = line.trim().split(/\s+/);
                return {
                    processId: parseInt(parts[1], 10),
                    processString: line
                };
            });

            res.status(200).json(processes);
        } catch (regexError) {
            res.status(400).json({
                code: 400,
                message: 'Invalid regular expression'
            });
        }
    });
});

app.listen(5000, '0.0.0.0', () => {
    console.log('Server is running on http://0.0.0.0:5000');
});