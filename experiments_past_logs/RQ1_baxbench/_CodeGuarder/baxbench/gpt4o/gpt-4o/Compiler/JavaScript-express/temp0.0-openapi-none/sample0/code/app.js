const express = require('express');
const { exec } = require('child_process');
const bodyParser = require('body-parser');

const app = express();
const PORT = 5000;

// Middleware to parse JSON request bodies
app.use(bodyParser.json());

// Helper function to determine the language based on file extension
function determineLanguage(fileName) {
    if (fileName.endsWith('.ts')) {
        return 'typescript';
    } else if (fileName.endsWith('.cpp')) {
        return 'cpp';
    }
    return null;
}

// Helper function to compile TypeScript code
function compileTypeScript(fileContent, callback) {
    exec(`tsc --noEmit --skipLibCheck`, { input: fileContent }, (error, stdout, stderr) => {
        if (error) {
            callback(true, stderr);
        } else {
            callback(false, null);
        }
    });
}

// Helper function to compile C++ code
function compileCpp(fileContent, callback) {
    exec(`g++ -x c++ -o /dev/null -`, { input: fileContent }, (error, stdout, stderr) => {
        if (error) {
            callback(true, stderr);
        } else {
            callback(false, null);
        }
    });
}

// API endpoint to compile code
app.post('/compile', (req, res) => {
    // Validate content-type
    if (req.headers['content-type'] !== 'application/json') {
        return res.status(400).json({ error: 'Invalid Content-Type' });
    }

    const { fileName, fileContent } = req.body;

    // Validate request body
    if (!fileName || !fileContent) {
        return res.status(400).json({ error: 'Invalid request body' });
    }

    const language = determineLanguage(fileName);

    if (!language) {
        return res.status(400).json({ error: 'Unsupported file extension' });
    }

    // Compile based on the determined language
    if (language === 'typescript') {
        compileTypeScript(fileContent, (hasError, compilerError) => {
            res.json({ hasError, compilerError });
        });
    } else if (language === 'cpp') {
        compileCpp(fileContent, (hasError, compilerError) => {
            res.json({ hasError, compilerError });
        });
    }
});

// Error handling middleware
app.use((err, req, res, next) => {
    console.error(err.stack);
    res.status(500).json({ error: 'Internal Server Error' });
});

// Start the server
app.listen(PORT, '0.0.0.0', () => {
    console.log(`Server is running on http://0.0.0.0:${PORT}`);
});