import { Controller, Get, Post, Body, HttpCode } from '@nestjs/common';
import { AppService } from './app.service';

@Controller()
export class AppController {
  constructor(private readonly appService: AppService) {}

  @Post('log')
  @HttpCode(200)
  logMessage(@Body('message') message: string): void {
    this.appService.logMessage(message);
  }

  @Get('logs')
  getLogs(): string {
    return this.appService.getLogs();
  }
}