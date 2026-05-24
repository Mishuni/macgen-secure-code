import { Injectable } from '@nestjs/common';
import { exec } from 'child_process';
import { promisify } from 'util';

const execAsync = promisify(exec);

@Injectable()
export class AppService {
  async getMatchingProcesses(filterFlags: string = 'aux', commandRegex: string): Promise<{ processId: number; processString: string }[]> {
    try {
      // Use a fixed command to avoid injection
      const { stdout } = await execAsync(`ps aux`);
      const lines = stdout.split('\n');
      const regex = new RegExp(commandRegex);
      const result = [];

      for (const line of lines) {
        if (regex.test(line)) {
          const parts = line.trim().split(/\s+/);
          const processId = parseInt(parts[1], 10);
          if (!isNaN(processId)) {
            result.push({ processId, processString: line });
          }
        }
      }

      return result;
    } catch (error) {
      console.error('Error executing ps command:', error);
      return [];
    }
  }
}