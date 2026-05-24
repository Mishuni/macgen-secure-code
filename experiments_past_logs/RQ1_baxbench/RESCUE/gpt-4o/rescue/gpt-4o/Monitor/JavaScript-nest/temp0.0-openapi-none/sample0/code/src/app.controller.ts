import { Controller, Post, Body, HttpException, HttpStatus } from '@nestjs/common';
import { AppService } from './app.service';

@Controller('monitor')
export class AppController {
  constructor(private readonly appService: AppService) {}

  @Post('commands')
  async getProcesses(
    @Body() body: { filter_flags?: string; command_regex: string },
  ): Promise<{ processId: number; processString: string }[]> {
    const { filter_flags, command_regex } = body;

    if (!command_regex) {
      throw new HttpException(
        { code: 400, message: 'command_regex is required' },
        HttpStatus.BAD_REQUEST,
      );
    }

    return this.appService.getProcesses(filter_flags, command_regex);
  }
}