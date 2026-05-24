const Koa = require('koa');
const Router = require('koa-router');
const multer = require('@koa/multer');
const fs = require('fs');
const path = require('path');
const { exec } = require('child_process');
const util = require('util');
const os = require('os');

// Promisify exec for easier async/await usage
const execPromise = util.promisify(exec);

const app = new Koa();
const router = new Router();
const upload = multer({ dest: os.tmpdir() }); // Use a secure temporary directory for file uploads

// Helper function to safely delete temporary files
const deleteFile = async (filePath) => {
  try {
    await fs.promises.unlink(filePath);
  } catch (err) {
    console.error(`Failed to delete file: ${filePath}`, err);
  }
};

// Route to handle PDF concatenation
router.post('/concatenate', upload.array('files'), async (ctx) => {
  const files = ctx.files;

  if (!files || files.length < 2) {
    ctx.status = 400;
    ctx.body = { error: 'Invalid input or missing files. At least two PDF files are required.' };
    return;
  }

  // Validate that all uploaded files are PDFs
  for (const file of files) {
    if (path.extname(file.originalname).toLowerCase() !== '.pdf') {
      ctx.status = 400;
      ctx.body = { error: 'All uploaded files must be PDFs.' };
      return;
    }
  }

  // Create a temporary file for the concatenated PDF
  const outputFilePath = path.join(os.tmpdir(), `concatenated_${Date.now()}.pdf`);

  try {
    // Prepare the list of input file paths
    const inputFilePaths = files.map((file) => file.path);

    // Use pdfunite to concatenate the PDF files
    const command = `pdfunite ${inputFilePaths.join(' ')} ${outputFilePath}`;
    await execPromise(command);

    // Read the concatenated PDF and send it as the response
    ctx.set('Content-Type', 'application/pdf');
    ctx.body = fs.createReadStream(outputFilePath);
  } catch (err) {
    console.error('Error during PDF concatenation:', err);
    ctx.status = 500;
    ctx.body = { error: 'An error occurred while processing the files.' };
  } finally {
    // Cleanup: Delete all temporary files
    for (const file of files) {
      await deleteFile(file.path);
    }
    await deleteFile(outputFilePath);
  }
});

// Register the router
app.use(router.routes()).use(router.allowedMethods());

// Start the server
const PORT = 5000;
app.listen(PORT, '0.0.0.0', () => {
  console.log(`Server running on http://0.0.0.0:${PORT}`);
});