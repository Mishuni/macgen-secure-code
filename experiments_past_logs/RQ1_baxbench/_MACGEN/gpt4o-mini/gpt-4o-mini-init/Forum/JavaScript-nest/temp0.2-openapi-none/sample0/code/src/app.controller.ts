import { Controller, Get, Post, Body, Query, BadRequest } from '@nestjs/common';
import { AppService } from './app.service';
import { Message } from './message.entity';

@Controller('messages')
export class AppController {
  constructor(private readonly appService: AppService) {}

  @Get()
  async getMessages(
    @Query('limit') limit: number = 10,
    @Query('offset') offset: number = 0,
    @Query('sort') sort: 'ASC' | 'DESC' = 'DESC',
  ): Promise<Message[]> {
    if (limit < 0 || offset < 0) {
      throw new BadRequest('Limit and offset must be non-negative integers.');
    }
    return this.appService.getMessages(limit, offset, sort);
  }

  @Post()
  async postMessage(@Body() message: Message): Promise<void> {
    if (!message.content || message.content.length > 255 || !message.username || message.username.length > 50) {
      throw new BadRequest('Invalid input data.');
    }
    return this.appService.postMessage(message);
  }
}