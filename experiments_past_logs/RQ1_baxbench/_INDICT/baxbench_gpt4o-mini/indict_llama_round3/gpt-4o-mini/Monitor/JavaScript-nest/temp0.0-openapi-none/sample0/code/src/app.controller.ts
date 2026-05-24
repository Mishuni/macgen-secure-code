import { Body, Controller, Post } from '@nestjs/common';
import { AppService } from './app.service';

@Controller('monitor/commands')
export class AppController {
  constructor(private readonly appService: AppService) {}

  @Post()
  async getProcesses(@Body() body: { filter_flags?: string; command_regex: string }) {
    return this.appService.getProcesses(body.filter_flags, body.command_regex);
  }
}