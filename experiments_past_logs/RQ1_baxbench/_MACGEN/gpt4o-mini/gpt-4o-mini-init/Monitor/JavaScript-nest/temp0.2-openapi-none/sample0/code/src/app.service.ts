import { Injectable } from '@nestjs/common';
import { exec } from 'child_process';
import { promisify } from 'util';

const execPromise = promisify(exec);

@Injectable()
export class AppService {
  async getProcesses(filter_flags: string, command_regex: string) {
    const command = `ps ${filter_flags} | grep -E '${command_regex}'`;
    const { stdout } = await execPromise(command);
    const processes = stdout.split('\n').filter(Boolean).map(line => {
      const parts = line.trim().split(/\s+/);
      return {
        processId: parseInt(parts[0], 10),
        processString: line.trim(),
      };
    });
    return processes;
  }
}