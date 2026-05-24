const express = require('express');
const multer = require('multer');
const fs = require('fs');
const path = require('path');
const { v4: uuidv4 } = require('uuid');
const PDFMerger = require('pdf-merger-js');
const pdfParse = require('pdf-parse');
const tmp = require('tmp');
const helmet = require('helmet');

const app = express();
app.use(helmet());

const upload = multer({
    dest: 'uploads/',
    fileFilter: (req, file, cb) => {
        if (file.mimetype !== 'application/pdf') {
            return cb(new Error('Only PDF files are allowed!'), false);
        }
        cb(null, true);
    },
    limits: { fileSize: 5 * 1024 * 1024, files: 10 } // Limit to 5MB per file and 10 files max
});

app.post('/concatenate', upload.array('files'), async (req, res) => {
    if (!req.files || req.files.length === 0) {
        return res.status(400).json({ error: "Invalid input or missing files." });
    }

    const pdfFiles = [];
    const merger = new PDFMerger();

    try {
        for (const file of req.files) {
            const fileBuffer = fs.readFileSync(file.path);
            const pdfData = await pdfParse(fileBuffer);

            if (!pdfData || !pdfData.numpages) {
                throw new Error("Invalid PDF file.");
            }

            pdfFiles.push(file.path);
            await merger.add(file.path);
        }

        const outputFilePath = tmp.tmpNameSync({ postfix: '.pdf' });
        await merger.save(outputFilePath);

        res.setHeader('Content-Type', 'application/pdf');
        res.sendFile(path.resolve(outputFilePath), err => {
            if (err) {
                console.error('Error sending file:', err);
                res.status(500).json({ error: "An error occurred while sending the file." });
            }

            // Clean up the concatenated file
            fs.unlink(outputFilePath, err => {
                if (err) console.error(`Error deleting file ${outputFilePath}:`, err);
            });
        });
    } catch (error) {
        console.error('Error during PDF processing:', error.message);
        res.status(500).json({ error: "An error occurred while processing the files." });
    } finally {
        // Clean up uploaded files
        pdfFiles.forEach(file => fs.unlink(file, err => {
            if (err) console.error(`Error deleting file ${file}:`, err);
        }));
    }
});

app.listen(5000, '127.0.0.1', () => {
    console.log('PDF Concatenation Service running on http://127.0.0.1:5000');
});