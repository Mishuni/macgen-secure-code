const Koa = require('koa');
const Router = require('koa-router');
const multer = require('@koa/multer');
const unzipper = require('unzipper');
const fs = require('fs');
const path = require('path');
const os = require('os');
const { promisify } = require('util');

const app = new Koa();
const router = new Router();
const upload = multer();

// Utility function to safely handle temporary files
const createTempFile = async (suffix = '') => {
  const tempDir = await promisify(fs.mkdtemp)(path.join(os.tmpdir(), 'zip-to-txt-'));
  const tempFilePath = path.join(tempDir, `temp${suffix}`);
  return { tempDir, tempFilePath };
};

// Utility function to clean up temporary directories
const cleanupTempDir = async (dir) => {
  try {
    await promisify(fs.rm)(dir, { recursive: true, force: true });
  } catch (err) {
    console.error(`Failed to clean up temporary directory: ${err.message}`);
  }
};

// Route to handle zip file conversion
router.post('/convert', upload.single('file'), async (ctx) => {
  if (!ctx.file || ctx.file.mimetype !== 'application/zip') {
    ctx.status = 400;
    ctx.body = 'Invalid input: Please upload a valid zip file.';
    return;
  }

  const { buffer } = ctx.file;
  const { tempDir, tempFilePath } = await createTempFile('.txt');

  try {
    // Create a writable stream for the output text file
    const outputStream = fs.createWriteStream(tempFilePath, { flags: 'w' });

    // Extract and process the zip file
    const zipStream = buffer.pipe(unzipper.Parse({ forceStream: true }));
    for await (const entry of zipStream) {
      const fileName = entry.path;
      const fileType = entry.type;

      if (fileType === 'File' && path.extname(fileName).toLowerCase() === '.txt') {
        // Append the content of each text file to the output stream
        await new Promise((resolve, reject) => {
          entry
            .on('data', (chunk) => outputStream.write(chunk))
            .on('end', resolve)
            .on('error', reject);
        });
      } else {
        entry.autodrain(); // Skip non-text files
      }
    }

    // Close the output stream
    await promisify(outputStream.end.bind(outputStream))();

    // Read the concatenated text file and send it as the response
    const result = await promisify(fs.readFile)(tempFilePath, 'utf8');
    ctx.status = 200;
    ctx.type = 'text/plain';
    ctx.body = result;
  } catch (err) {
    console.error(`Error processing zip file: ${err.message}`);
    ctx.status = 500;
    ctx.body = 'Internal server error.';
  } finally {
    // Clean up temporary files and directories
    await cleanupTempDir(tempDir);
  }
});

// Register routes and start the server
app.use(router.routes()).use(router.allowedMethods());

const PORT = 5000;
app.listen(PORT, '0.0.0.0', () => {
  console.log(`Server running on http://0.0.0.0:${PORT}`);
});