import { Controller, Post, Body, BadRequestException } from '@nestjs/common';
import { AppService } from './app.service';

@Controller('monitor/commands')
export class AppController {
  constructor(private readonly appService: AppService) {}

  @Post()
  async getProcesses(@Body() body: { filter_flags: string; command_regex: string }) {
    const { filter_flags, command_regex } = body;

    // Validate filter_flags with improved regex
    if (!/^[a-zA-Z]{1,2}(\s+-[a-zA-Z]+)*$/.test(filter_flags)) {
      throw new BadRequestException('Invalid filter flags');
    }

    // Sanitize command_regex and limit its length
    const sanitizedCommandRegex = command_regex.replace(/[^a-zA-Z0-9._*?+|()\\[\\]{}]/g, '').slice(0, 100);
    return this.appService.getProcesses(filter_flags, sanitizedCommandRegex);
  }
}