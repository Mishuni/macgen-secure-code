import { Controller, Get, Post, Body } from '@nestjs/common';
import { AppService } from './app.service';

@Controller()
export class AppController {
  constructor(private readonly appService: AppService) {}

  @Post('log')
  logMessage(@Body('message') message: string): string {
    const sanitizedMessage = this.appService.sanitizeMessage(message);
    this.appService.logMessage(sanitizedMessage);
    return 'Log message successful';
  }

  @Get('logs')
  getLogs(): string {
    return this.appService.getLogs();
  }
}