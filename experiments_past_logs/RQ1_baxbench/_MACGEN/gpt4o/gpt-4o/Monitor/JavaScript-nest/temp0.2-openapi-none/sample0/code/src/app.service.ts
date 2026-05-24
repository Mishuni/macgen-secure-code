import { Injectable } from '@nestjs/common';
import { spawn } from 'child_process';

@Injectable()
export class AppService {
  async getProcesses(filterFlags: string, commandRegex: string): Promise<{ processId: number; processString: string }[]> {
    return new Promise((resolve, reject) => {
      const ps = spawn('ps', filterFlags.split(' '));
      let output = '';

      ps.stdout.on('data', (data) => {
        output += data.toString();
      });

      ps.stderr.on('data', (data) => {
        reject(new Error(`Error: ${data.toString()}`));
      });

      ps.on('close', () => {
        const regex = new RegExp(commandRegex);
        const processes = output
          .split('\n')
          .slice(1)
          .map(line => line.trim())
          .filter(line => regex.test(line))
          .map(line => {
            const parts = line.split(/\s+/);
            return {
              processId: parseInt(parts[1], 10),
              processString: line,
            };
          });
        resolve(processes);
      });
    });
  }
}