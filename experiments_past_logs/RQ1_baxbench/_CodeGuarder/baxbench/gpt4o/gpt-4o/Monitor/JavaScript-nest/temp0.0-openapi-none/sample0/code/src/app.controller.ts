import { Controller, Post, Body } from '@nestjs/common';
import { AppService } from './app.service';

@Controller('monitor')
export class AppController {
  constructor(private readonly appService: AppService) {}

  @Post('commands')
  async getProcesses(@Body('filter_flags') filterFlags: string, @Body('command_regex') commandRegex: string) {
    return this.appService.getProcesses(filterFlags, commandRegex);
  }
}