import { Injectable } from '@nestjs/common';
import { exec } from 'child_process';
import { promisify } from 'util';

const execPromise = promisify(exec);

@Injectable()
export class AppService {
  async concatenatePDFs(inputFiles: string[], outputFile: string): Promise<void> {
    const command = `pdfunite ${inputFiles.join(' ')} ${outputFile}`;
    await execPromise(command);
  }
}