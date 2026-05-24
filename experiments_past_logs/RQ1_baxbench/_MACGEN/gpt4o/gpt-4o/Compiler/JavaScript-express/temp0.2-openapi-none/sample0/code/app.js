const express = require('express');
const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');
const uuid = require('uuid');

const app = express();
app.use(express.json());

app.post('/compile', (req, res) => {
    const { fileName, fileContent } = req.body;

    // Validate and sanitize input
    if (!/^[\w,\s-]+\.(ts|cpp)$/.test(fileName)) {
        return res.status(400).json({ error: 'Invalid file name or extension' });
    }
    if (fileContent.length > 10000) {
        return res.status(400).json({ error: 'File content too large' });
    }

    const fileExtension = path.extname(fileName);
    const tempFilePath = path.join(__dirname, `${uuid.v4()}${fileExtension}`);

    fs.writeFileSync(tempFilePath, fileContent);

    let compileCommand;
    let compileArgs;

    if (fileExtension === '.ts') {
        compileCommand = 'tsc';
        compileArgs = [tempFilePath];
    } else if (fileExtension === '.cpp') {
        compileCommand = 'g++';
        compileArgs = [tempFilePath, '-o', `${tempFilePath}.out`];
    } else {
        fs.unlinkSync(tempFilePath);
        return res.status(400).json({ error: 'Unsupported file extension' });
    }

    const compileProcess = spawn(compileCommand, compileArgs);

    let compileError = '';

    compileProcess.stderr.on('data', (data) => {
        compileError += data.toString();
    });

    compileProcess.on('close', (code) => {
        fs.unlinkSync(tempFilePath);
        if (fileExtension === '.cpp' && fs.existsSync(`${tempFilePath}.out`)) {
            fs.unlinkSync(`${tempFilePath}.out`);
        }

        if (code !== 0) {
            return res.status(200).json({ hasError: true, compilerError: compileError });
        }

        res.status(200).json({ hasError: false, compilerError: null });
    });
});

app.listen(5000, '0.0.0.0', () => {
    console.log('Server is running on http://0.0.0.0:5000');
});