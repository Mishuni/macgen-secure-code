import { Controller, Post, Body, Get } from '@nestjs/common';
import { AppService } from './app.service';

@Controller()
export class AppController {
  constructor(private readonly appService: AppService) {}

  @Post('log')
  logMessage(@Body() body: { message: string }): string {
    try {
      return this.appService.logMessage(body.message);
    } catch (error) {
      return error.message; // Handle error gracefully
    }
  }

  @Get('logs')
  getLogs(): string {
    return this.appService.getLogs();
  }
}