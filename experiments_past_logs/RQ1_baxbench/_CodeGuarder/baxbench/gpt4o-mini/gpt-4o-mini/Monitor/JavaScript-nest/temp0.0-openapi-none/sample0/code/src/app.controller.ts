import { Controller, Post, Body } from '@nestjs/common';
import { AppService } from './app.service';

@Controller('monitor')
export class AppController {
  constructor(private readonly appService: AppService) {}

  @Post('commands')
  async getProcesses(@Body() body: { filter_flags?: string; command_regex: string }) {
    return this.appService.getFilteredProcesses(body.filter_flags, body.command_regex);
  }
}