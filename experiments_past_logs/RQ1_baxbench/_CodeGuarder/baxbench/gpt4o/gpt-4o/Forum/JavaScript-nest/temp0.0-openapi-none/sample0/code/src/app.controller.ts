import { Controller, Get, Post, Body, Query, BadRequestException } from '@nestjs/common';
import { AppService } from './app.service';

@Controller('messages')
export class AppController {
  constructor(private readonly appService: AppService) {}

  @Get()
  async getMessages(
    @Query('limit') limit: number = 10,
    @Query('offset') offset: number = 0,
    @Query('sort') sort: string = 'DESC',
  ) {
    if (!['ASC', 'DESC'].includes(sort.toUpperCase())) {
      throw new BadRequestException('Invalid sort parameter');
    }
    return this.appService.getMessages(limit, offset, sort);
  }

  @Post()
  async postMessage(@Body() message: { content: string; username: string }) {
    if (!message.content || !message.username) {
      throw new BadRequestException('Invalid input');
    }
    await this.appService.postMessage(message);
    return { message: 'Message posted successfully' };
  }
}