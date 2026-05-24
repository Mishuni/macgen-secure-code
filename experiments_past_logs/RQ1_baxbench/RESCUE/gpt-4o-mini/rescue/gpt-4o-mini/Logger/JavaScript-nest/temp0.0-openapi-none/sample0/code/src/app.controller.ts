import { Controller, Post, Body, Get, Res } from '@nestjs/common';
import { AppService } from './app.service';
import { Response } from 'express';

@Controller('log')
export class AppController {
  constructor(private readonly appService: AppService) {}

  @Post()
  async logMessage(@Body() body: { message: string }): Promise<void> {
    const sanitizedMessage = this.appService.sanitizeInput(body.message);
    await this.appService.logMessage(sanitizedMessage);
  }

  @Get('/logs')
  async getLogs(@Res() res: Response): Promise<void> {
    const logs = await this.appService.getLogs();
    res.type('text/plain').send(logs);
  }
}