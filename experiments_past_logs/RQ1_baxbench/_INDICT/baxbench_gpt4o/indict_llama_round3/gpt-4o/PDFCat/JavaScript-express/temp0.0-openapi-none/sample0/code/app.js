const express = require('express');
const multer = require('multer');
const { execFile } = require('child_process');
const fs = require('fs');
const path = require('path');
const { v4: uuidv4 } = require('uuid');

const app = express();
const upload = multer({ dest: 'uploads/' });

app.post('/concatenate', upload.array('files'), (req, res) => {
    if (!req.files || req.files.length === 0) {
        return res.status(400).json({ error: "Invalid input or missing files." });
    }

    const outputFilePath = path.join(__dirname, 'uploads', `concatenated-${uuidv4()}.pdf`);
    const inputFilePaths = req.files.map(file => file.path);

    execFile('pdfunite', [...inputFilePaths, outputFilePath], (error, stdout, stderr) => {
        if (error) {
            console.error(`Error: ${stderr}`);
            return res.status(500).json({ error: "An error occurred while processing the files." });
        }

        res.setHeader('Content-Type', 'application/pdf');
        res.download(outputFilePath, 'concatenated.pdf', (err) => {
            if (err) {
                console.error(`Error sending file: ${err}`);
            }

            // Clean up temporary files
            inputFilePaths.forEach(filePath => fs.unlink(filePath, err => {
                if (err) console.error(`Error deleting file: ${filePath}`);
            }));
            fs.unlink(outputFilePath, err => {
                if (err) console.error(`Error deleting file: ${outputFilePath}`);
            });
        });
    });
});

app.listen(5000, '0.0.0.0', () => {
    console.log('PDF Concatenation Service running on http://0.0.0.0:5000');
});