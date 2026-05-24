import { Injectable, HttpException, HttpStatus } from '@nestjs/common';
import { spawn } from 'child_process';

@Injectable()
export class AppService {
  async getProcesses(
    filterFlags: string | undefined,
    commandRegex: string,
  ): Promise<{ processId: number; processString: string }[]> {
    return new Promise((resolve, reject) => {
      const args = filterFlags ? filterFlags.split(' ') : ['aux'];
      const ps = spawn('ps', args);

      let output = '';
      let errorOutput = '';

      ps.stdout.on('data', (data) => {
        output += data.toString();
      });

      ps.stderr.on('data', (data) => {
        errorOutput += data.toString();
      });

      ps.on('close', (code) => {
        if (code !== 0) {
          reject(
            new HttpException(
              { code: 500, message: `ps command failed: ${errorOutput}` },
              HttpStatus.INTERNAL_SERVER_ERROR,
            ),
          );
          return;
        }

        try {
          const regex = new RegExp(commandRegex);
          const processes = output
            .split('\n')
            .slice(1) // Skip the header row
            .filter((line) => regex.test(line))
            .map((line) => {
              const columns = line.trim().split(/\s+/);
              const processId = parseInt(columns[1], 10); // PID is usually the second column
              const processString = line.trim();
              return { processId, processString };
            });

          resolve(processes);
        } catch (err) {
          reject(
            new HttpException(
              { code: 400, message: `Invalid command_regex: ${err.message}` },
              HttpStatus.BAD_REQUEST,
            ),
          );
        }
      });
    });
  }
}