import { Controller, Get, Post, Query, Body, Res, HttpException, HttpStatus } from '@nestjs/common';
import { AppService } from './app.service';
import { Response } from 'express';

@Controller('messages')
export class AppController {
  constructor(private readonly appService: AppService) {}

  @Get()
  async getMessages(
    @Query('limit') limit: number = 10,
    @Query('offset') offset: number = 0,
    @Query('sort') sort: 'ASC' | 'DESC' = 'DESC',
    @Res() res: Response,
  ) {
    try {
      const messages = await this.appService.getMessages(limit, offset, sort);
      res.status(HttpStatus.OK).send(messages);
    } catch (error) {
      throw new HttpException('Internal Server Error', HttpStatus.INTERNAL_SERVER_ERROR);
    }
  }

  @Post()
  async postMessage(@Body() body: { content: string; username: string }, @Res() res: Response) {
    const { content, username } = body;

    if (!content || !username) {
      throw new HttpException('Invalid input', HttpStatus.BAD_REQUEST);
    }

    try {
      await this.appService.postMessage(content, username);
      res.status(HttpStatus.OK).send({ message: 'Message posted successfully' });
    } catch (error) {
      throw new HttpException('Internal Server Error', HttpStatus.INTERNAL_SERVER_ERROR);
    }
  }
}