import { Controller, Get, Post, Body, Query, Res, HttpStatus } from '@nestjs/common';
import { AppService } from './app.service';
import { Response } from 'express';

@Controller('messages')
export class AppController {
  constructor(private readonly appService: AppService) {}

  @Get()
  async getMessages(
    @Query('limit') limit: number = 10,
    @Query('offset') offset: number = 0,
    @Query('sort') sort: string = 'DESC',
    @Res() res: Response
  ) {
    const messages = await this.appService.getMessages(limit, offset, sort);
    res.status(HttpStatus.OK).send(messages);
  }

  @Post()
  async postMessage(@Body() message: { content: string; username: string }, @Res() res: Response) {
    try {
      await this.appService.postMessage(message);
      res.status(HttpStatus.OK).send({ message: 'Message posted successfully' });
    } catch (error) {
      res.status(HttpStatus.BAD_REQUEST).send({ message: 'Invalid input' });
    }
  }
}