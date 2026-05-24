import Koa from 'koa';
import Router from 'koa-router';
import multer from '@koa/multer';
import { execFile } from 'child_process';
import fs from 'fs';
import path from 'path';
import util from 'util';

const app = new Koa();
const router = new Router();
const upload = multer({ dest: 'uploads/' });
const execFilePromise = util.promisify(execFile);

router.post('/concatenate', upload.array('files'), async (ctx) => {
  try {
    const files = ctx.files;
    if (!files || files.length === 0) {
      ctx.status = 400;
      ctx.body = { error: "Invalid input or missing files." };
      return;
    }

    const inputFiles = files.map(file => file.path);
    const outputFilePath = path.join('uploads', `concatenated_${Date.now()}.pdf`);

    try {
      await execFilePromise('pdfunite', [...inputFiles, outputFilePath]);
      ctx.set('Content-Type', 'application/pdf');
      ctx.body = fs.createReadStream(outputFilePath);
    } catch (error) {
      ctx.status = 500;
      ctx.body = { error: "An error occurred while processing the files." };
    } finally {
      // Clean up uploaded files
      inputFiles.forEach(file => {
        if (fs.existsSync(file)) {
          fs.unlinkSync(file);
        }
      });
      if (fs.existsSync(outputFilePath)) {
        fs.unlinkSync(outputFilePath);
      }
    }
  } catch (error) {
    ctx.status = 500;
    ctx.body = { error: "An error occurred while processing the files." };
  }
});

app.use(router.routes()).use(router.allowedMethods());

app.listen(5000, () => {
  console.log('Server running on http://0.0.0.0:5000');
});