const express = require('express');
const { exec } = require('child_process');
const bodyParser = require('body-parser');

const app = express();
app.use(bodyParser.json());

app.post('/monitor/commands', (req, res) => {
    // Validate content-type
    if (req.headers['content-type'] !== 'application/json') {
        return res.status(400).json({ code: 400, message: 'Invalid content-type' });
    }

    const { filter_flags, command_regex } = req.body;

    // Validate command_regex
    if (!command_regex || typeof command_regex !== 'string') {
        return res.status(400).json({ code: 400, message: 'Invalid command_regex' });
    }

    // Construct the command safely
    const psCommand = ['ps', filter_flags || 'aux'];
    const grepCommand = ['grep', '-E', command_regex];

    // Execute the command
    exec(`${psCommand.join(' ')} | ${grepCommand.join(' ')}`, (error, stdout, stderr) => {
        if (error) {
            console.error(`exec error: ${error}`);
            return res.status(500).json({ code: 500, message: 'Internal server error' });
        }

        if (stderr) {
            console.error(`stderr: ${stderr}`);
            return res.status(500).json({ code: 500, message: 'Internal server error' });
        }

        // Parse the output
        const processes = stdout.split('\n').filter(line => line.trim() !== '').map(line => {
            const parts = line.trim().split(/\s+/);
            return {
                processId: parseInt(parts[1], 10),
                processString: line
            };
        });

        res.status(200).json(processes);
    });
});

app.listen(5000, '0.0.0.0', () => {
    console.log('Server is running on http://0.0.0.0:5000');
});