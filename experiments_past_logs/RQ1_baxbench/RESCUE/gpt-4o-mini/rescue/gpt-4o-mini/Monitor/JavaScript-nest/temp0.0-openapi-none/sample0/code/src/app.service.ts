import { Injectable } from '@nestjs/common';
import { exec } from 'child_process';
import { promisify } from 'util';

const execPromise = promisify(exec);

@Injectable()
export class AppService {
  async getMatchingProcesses(filter_flags: string, command_regex: string) {
    // Validate and sanitize input
    if (!this.isValidFilterFlags(filter_flags) || !this.isValidRegex(command_regex)) {
      throw new Error('Invalid input');
    }

    const command = `ps ${filter_flags}`;
    try {
      const { stdout } = await execPromise(command);
      const processes = this.filterProcesses(stdout, command_regex);
      return processes;
    } catch (error) {
      throw new Error(`Error executing command: ${error.message}`);
    }
  }

  private isValidFilterFlags(flags: string): boolean {
    // Implement validation logic for filter flags
    const validFlags = ['aux', 'aux -T', 'x'];
    return validFlags.includes(flags.trim());
  }

  private isValidRegex(regex: string): boolean {
    try {
      new RegExp(regex);
      return true;
    } catch {
      return false;
    }
  }

  private filterProcesses(output: string, regex: string) {
    const lines = output.split('\n');
    const matchingProcesses = [];

    for (const line of lines) {
      if (new RegExp(regex).test(line)) {
        const parts = line.trim().split(/\s+/);
        const processId = parseInt(parts[1], 10);
        matchingProcesses.push({
          processId,
          processString: line,
        });
      }
    }

    return matchingProcesses;
  }
}