import { Controller, Post, Body, Get, Res, HttpException, HttpStatus } from '@nestjs/common';
import { AppService } from './app.service';
import { Response } from 'express';

@Controller()
export class AppController {
  constructor(private readonly appService: AppService) {}

  @Post('log')
  logMessage(@Body() body: { message: string }): string {
    if (!body.message || typeof body.message !== 'string') {
      throw new HttpException('Invalid message', HttpStatus.BAD_REQUEST);
    }
    this.appService.logMessage(body.message);
    return 'Log message successful';
  }

  @Get('logs')
  getLogs(@Res() res: Response): void {
    const logs = this.appService.getLogs();
    res.type('text/plain').send(logs);
  }
}