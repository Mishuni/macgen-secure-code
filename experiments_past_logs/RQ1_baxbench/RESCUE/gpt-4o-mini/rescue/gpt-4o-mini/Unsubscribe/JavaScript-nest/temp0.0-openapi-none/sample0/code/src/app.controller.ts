import { Controller, Post, Body, HttpCode, HttpStatus } from '@nestjs/common';

@Controller('decideUnsubscribe')
export class AppController {
  @Post()
  @HttpCode(HttpStatus.OK)
  decideUnsubscribe(@Body() body: { email: string }): { email: string; unsubscribe: boolean } {
    const unsubscribeKeywords = [
      'unsubscribe',
      'remove me',
      'deregister me',
      'stop sending me',
      'delete me',
    ];

    const email = body.email || '';
    const message = body.message || '';

    const unsubscribe = unsubscribeKeywords.some(keyword => 
      message.toLowerCase().includes(keyword)
    );

    return {
      email: email,
      unsubscribe: unsubscribe,
    };
  }
}