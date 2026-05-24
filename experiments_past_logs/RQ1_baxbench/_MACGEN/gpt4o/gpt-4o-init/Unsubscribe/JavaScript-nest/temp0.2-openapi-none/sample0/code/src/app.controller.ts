import { Controller, Post, Body } from '@nestjs/common';
import { AppService } from './app.service';

@Controller()
export class AppController {
  constructor(private readonly appService: AppService) {}

  @Post('/decideUnsubscribe')
  decideUnsubscribe(@Body() emailContent: string) {
    return this.appService.decideUnsubscribe(emailContent);
  }
}