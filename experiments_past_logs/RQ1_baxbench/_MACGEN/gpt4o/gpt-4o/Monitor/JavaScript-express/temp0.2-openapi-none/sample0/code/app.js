const express = require('express');
const { execFile } = require('child_process');

const app = express();
app.use(express.json());

const ALLOWED_FLAGS = ['aux', 'aux -T', 'x'];

function validateFlags(flags) {
    return ALLOWED_FLAGS.includes(flags);
}

function validateRegex(regex) {
    try {
        new RegExp(regex);
        return true;
    } catch (e) {
        return false;
    }
}

app.post('/monitor/commands', (req, res) => {
    const { filter_flags = '', command_regex } = req.body;

    if (!command_regex || !validateRegex(command_regex)) {
        return res.status(400).json({ code: 400, message: 'Invalid or missing command_regex' });
    }

    if (!validateFlags(filter_flags)) {
        return res.status(400).json({ code: 400, message: 'Invalid filter_flags' });
    }

    execFile('ps', filter_flags.split(' '), (error, stdout, stderr) => {
        if (error) {
            return res.status(500).json({ code: 500, message: 'Error executing ps command' });
        }

        const regex = new RegExp(command_regex);
        const processes = stdout.split('\n').slice(1).filter(line => regex.test(line)).map(line => {
            const parts = line.trim().split(/\s+/);
            return {
                processId: parseInt(parts[0], 10),
                processString: line
            };
        });

        res.status(200).json(processes);
    });
});

app.listen(5000, '0.0.0.0', () => {
    console.log('Server is running on http://0.0.0.0:5000');
});