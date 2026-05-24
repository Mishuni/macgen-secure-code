import { Controller, Post, Body, Get, Res } from '@nestjs/common';
import { AppService } from './app.service';
import { Response } from 'express';

@Controller('log')
export class AppController {
  constructor(private readonly appService: AppService) {}

  @Post()
  logMessage(@Body() body: { message: string }): string {
    return this.appService.logMessage(body.message);
  }

  @Get('/logs')
  getLogs(@Res() res: Response): void {
    const logs = this.appService.getLogs();
    res.type('text/plain').send(logs);
  }
}