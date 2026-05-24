import { Injectable } from '@nestjs/common';
import { exec } from 'child_process';
import { promisify } from 'util';
import * as fs from 'fs';
import * as path from 'path';
import { v4 as uuidv4 } from 'uuid';

const execAsync = promisify(exec);

@Injectable()
export class AppService {
  async convertPdfToText(file: Express.Multer.File): Promise<string> {
    const tempDir = path.join(__dirname, '..', 'uploads');
    const tempFilePath = path.join(tempDir, `${uuidv4()}.pdf`);
    const outputFilePath = path.join(tempDir, `${uuidv4()}.txt`);

    try {
      // Ensure the uploads directory exists
      if (!fs.existsSync(tempDir)) {
        fs.mkdirSync(tempDir, { recursive: true });
      }

      // Save the uploaded file to a temporary location
      fs.writeFileSync(tempFilePath, file.buffer);

      // Use the `pdftotext` utility to extract text from the PDF
      await execAsync(`pdftotext "${tempFilePath}" "${outputFilePath}"`);

      // Read the extracted text from the output file
      const extractedText = fs.readFileSync(outputFilePath, 'utf8');

      // Return the extracted text
      return extractedText;
    } catch (error) {
      throw new Error('Failed to convert PDF to text');
    } finally {
      // Clean up temporary files
      if (fs.existsSync(tempFilePath)) {
        fs.unlinkSync(tempFilePath);
      }
      if (fs.existsSync(outputFilePath)) {
        fs.unlinkSync(outputFilePath);
      }
    }
  }
}