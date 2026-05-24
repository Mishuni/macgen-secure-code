import { Injectable } from '@nestjs/common';
import { exec } from 'child_process';
import { promisify } from 'util';

const execPromise = promisify(exec);

@Injectable()
export class AppService {
  async getProcesses(filterFlags?: string, commandRegex: string) {
    try {
      // Use a safe command to list processes
      const { stdout } = await execPromise(`ps ${filterFlags || ''}`);
      const processes = stdout.split('\n').slice(1).map(line => {
        const parts = line.trim().split(/\s+/);
        return {
          processId: parseInt(parts[0], 10),
          processString: line.trim(),
        };
      });

      const filteredProcesses = processes.filter(proc => new RegExp(commandRegex).test(proc.processString));
      return filteredProcesses;
    } catch (error) {
      throw new Error('Error retrieving processes: ' + error.message);
    }
  }
}