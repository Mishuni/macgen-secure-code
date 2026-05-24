import { Controller, Get, Post, Body, BadRequestException } from '@nestjs/common';
import { AppService } from './app.service';

@Controller()
export class AppController {
  constructor(private readonly appService: AppService) {}

  @Post('log')
  async logMessage(@Body() body: { message: string }): Promise<{ message: string }> {
    if (!body.message || typeof body.message !== 'string') {
      throw new BadRequestException('Invalid message');
    }
    await this.appService.logMessage(body.message);
    return { message: 'Log message successful' };
  }

  @Get('logs')
  async getLogs(): Promise<string> {
    return this.appService.getLogs();
  }
}