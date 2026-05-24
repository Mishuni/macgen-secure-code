import { Controller, Post, Body, BadRequestException } from '@nestjs/common';
import { AppService } from './app.service';

@Controller('monitor')
export class AppController {
  constructor(private readonly appService: AppService) {}

  @Post('commands')
  async monitorProcesses(@Body() body: { filter_flags?: string; command_regex: string }) {
    if (!this.isValidRegex(body.command_regex)) {
      throw new BadRequestException('Invalid regular expression');
    }
    return this.appService.getMatchingProcesses(body.filter_flags, body.command_regex);
  }

  private isValidRegex(regex: string): boolean {
    try {
      new RegExp(regex);
      return true;
    } catch (e) {
      return false;
    }
  }
}