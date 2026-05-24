import { Controller, Post, Body } from '@nestjs/common';
import { AppService } from './app.service';

@Controller('monitor/commands')
export class AppController {
  constructor(private readonly appService: AppService) {}

  @Post()
  async getProcesses(@Body() body: { filter_flags: string; command_regex: string }) {
    const { filter_flags, command_regex } = body;

    // Validate filter_flags
    if (!/^[\w\s-]*$/.test(filter_flags)) {
      throw new Error('Invalid filter flags');
    }

    // Sanitize command_regex
    const sanitizedCommandRegex = command_regex.replace(/[^a-zA-Z0-9._*?+|()\\[\\]{}]/g, '');
    return this.appService.getProcesses(filter_flags, sanitizedCommandRegex);
  }
}