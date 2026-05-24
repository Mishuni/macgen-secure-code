import { Controller, Post, Body, Get } from '@nestjs/common';
import { AppService } from './app.service';

@Controller()
export class AppController {
  constructor(private readonly appService: AppService) {}

  @Post('log')
  logMessage(@Body() body: { message: string }): string {
    return this.appService.logMessage(body.message);
  }

  @Get('logs')
  getLogs(): string {
    return this.appService.getLogs();
  }
}