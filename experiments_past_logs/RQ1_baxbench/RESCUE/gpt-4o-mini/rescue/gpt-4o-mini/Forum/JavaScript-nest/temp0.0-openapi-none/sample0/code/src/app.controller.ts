import { Controller, Get, Post, Body, Query, Res } from '@nestjs/common';
import { AppService } from './app.service';
import { Response } from 'express';
import { Message } from './message.interface';

@Controller('messages')
export class AppController {
  constructor(private readonly appService: AppService) {}

  @Get()
  async getMessages(
    @Query('limit') limit: number = 10,
    @Query('offset') offset: number = 0,
    @Query('sort') sort: 'ASC' | 'DESC' = 'DESC',
    @Res() res: Response
  ) {
    const messages = await this.appService.getMessages(limit, offset, sort);
    res.setHeader('Content-Type', 'text/html');
    res.send(messages);
  }

  @Post()
  async postMessage(@Body() message: Message, @Res() res: Response) {
    if (!message.content || !message.username) {
      return res.status(400).send('Invalid input');
    }
    const savedMessage = await this.appService.saveMessage(message);
    res.status(200).send(savedMessage);
  }
}