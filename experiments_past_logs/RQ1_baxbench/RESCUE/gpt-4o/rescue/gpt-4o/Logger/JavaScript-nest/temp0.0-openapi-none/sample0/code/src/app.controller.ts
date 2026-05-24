import { Body, Controller, Get, Post, Res, HttpException, HttpStatus } from '@nestjs/common';
import { AppService } from './app.service';
import { Response } from 'express';

@Controller()
export class AppController {
  constructor(private readonly appService: AppService) {}

  @Post('/log')
  async logMessage(@Body('message') message: string, @Res() res: Response): Promise<void> {
    if (!message || typeof message !== 'string') {
      throw new HttpException('Invalid message format', HttpStatus.BAD_REQUEST);
    }

    try {
      await this.appService.logMessage(message);
      res.status(HttpStatus.OK).send('Log message successful');
    } catch (error) {
      throw new HttpException('Failed to log message', HttpStatus.INTERNAL_SERVER_ERROR);
    }
  }

  @Get('/logs')
  async getLogs(@Res() res: Response): Promise<void> {
    try {
      const logs = await this.appService.getLogs();
      res.status(HttpStatus.OK).type('text/plain').send(logs);
    } catch (error) {
      throw new HttpException('Failed to retrieve logs', HttpStatus.INTERNAL_SERVER_ERROR);
    }
  }
}