import { Injectable } from '@nestjs/common';
import { exec } from 'child_process';
import { promisify } from 'util';

const execPromise = promisify(exec);

@Injectable()
export class AppService {
  async getFilteredProcesses(filterFlags?: string, commandRegex: string) {
    const command = `ps ${filterFlags || ''} | grep -E '${commandRegex}'`;
    try {
      const { stdout } = await execPromise(command);
      const processes = stdout.split('\\n').filter(line => line.trim() !== '');
      return processes.map(line => {
        const parts = line.trim().split(/\s+/);
        return {
          processId: parseInt(parts[0], 10),
          processString: line.trim(),
        };
      });
    } catch (error) {
      console.error('Error executing command:', error);
      return [];
    }
  }
}