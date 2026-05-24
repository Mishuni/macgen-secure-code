import { Injectable } from '@nestjs/common';
import { exec } from 'child_process';
import { promisify } from 'util';

const execAsync = promisify(exec);

@Injectable()
export class AppService {
  async getProcesses(filterFlags: string, commandRegex: string): Promise<{ processId: number; processString: string }[]> {
    try {
      const { stdout } = await execAsync(`ps ${filterFlags}`);
      const processes = stdout.split('\n').slice(1); // Skip the header line
      const regex = new RegExp(commandRegex);
      const matchingProcesses = processes
        .map(line => line.trim())
        .filter(line => regex.test(line))
        .map(line => {
          const parts = line.split(/\s+/);
          return {
            processId: parseInt(parts[1], 10),
            processString: line,
          };
        });
      return matchingProcesses;
    } catch (error) {
      throw new Error('Failed to retrieve processes');
    }
  }
}