import { Controller, Get, Post, Body, Query } from '@nestjs/common';
import { AppService } from './app.service';
import { Message } from './message.interface';

@Controller('messages')
export class AppController {
  constructor(private readonly appService: AppService) {}

  @Get()
  async getMessages(
    @Query('limit') limit: number = 10,
    @Query('offset') offset: number = 0,
    @Query('sort') sort: 'ASC' | 'DESC' = 'DESC',
  ): Promise<Message[]> {
    return this.appService.getMessages(limit, offset, sort);
  }

  @Post()
  async postMessage(@Body() message: Message): Promise<void> {
    return this.appService.postMessage(message);
  }
}