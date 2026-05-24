const express = require('express');
const { execFile } = require('child_process');
const bodyParser = require('body-parser');

const app = express();
const PORT = 5000;

// Middleware to parse JSON request bodies
app.use(bodyParser.json());

// Helper function to validate input
function validateInput(filterFlags, commandRegex) {
    const filterFlagsPattern = /^[a-zA-Z0-9\s\-]*$/; // Allow only alphanumeric, spaces, and dashes
    try {
        new RegExp(commandRegex); // Validate if the regex is valid
    } catch (e) {
        return false;
    }
    return filterFlagsPattern.test(filterFlags);
}

// Route to handle POST requests to /monitor/commands
app.post('/monitor/commands', (req, res) => {
    const { filter_flags: filterFlags = '', command_regex: commandRegex } = req.body;

    // Validate input
    if (!commandRegex || !validateInput(filterFlags, commandRegex)) {
        return res.status(400).json({
            code: 400,
            message: 'Invalid input. Ensure filter_flags and command_regex are properly formatted.',
        });
    }

    // Construct the command arguments securely
    const args = ['-eo', 'pid,command']; // Use a safe and minimal set of arguments for `ps`
    if (filterFlags) {
        args.push(filterFlags);
    }

    // Execute the `ps` command securely
    execFile('ps', args, (error, stdout, stderr) => {
        if (error) {
            console.error('Error executing ps command:', error);
            return res.status(500).json({
                code: 500,
                message: 'Internal server error while retrieving processes.',
            });
        }

        if (stderr) {
            console.error('Error output from ps command:', stderr);
            return res.status(500).json({
                code: 500,
                message: 'Error occurred while processing the command.',
            });
        }

        // Parse the output of the `ps` command
        const processes = stdout
            .split('\n')
            .slice(1) // Skip the header line
            .map(line => line.trim())
            .filter(line => line) // Remove empty lines
            .map(line => {
                const [pid, ...commandParts] = line.split(/\s+/);
                return { pid: parseInt(pid, 10), command: commandParts.join(' ') };
            });

        // Filter processes based on the provided regex
        const regex = new RegExp(commandRegex);
        const filteredProcesses = processes.filter(proc => regex.test(proc.command));

        // Respond with the filtered processes
        const response = filteredProcesses.map(proc => ({
            processId: proc.pid,
            processString: proc.command,
        }));

        res.status(200).json(response);
    });
});

// Start the server
app.listen(PORT, '0.0.0.0', () => {
    console.log(`Server is running on http://0.0.0.0:${PORT}`);
});