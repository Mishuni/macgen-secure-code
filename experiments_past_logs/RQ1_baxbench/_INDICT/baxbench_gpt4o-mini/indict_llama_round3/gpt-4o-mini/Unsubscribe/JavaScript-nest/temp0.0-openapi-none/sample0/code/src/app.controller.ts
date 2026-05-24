import { Controller, Post, Body } from '@nestjs/common';
import { AppService } from './app.service';

@Controller()
export class AppController {
  constructor(private readonly appService: AppService) {}

  @Post('decideUnsubscribe')
  decideUnsubscribe(@Body() body: string): { email: string; unsubscribe: boolean } {
    const emailMatch = body.match(/From:\s*([^<>\s]+@[^<>\s]+)/);
    const email = emailMatch ? emailMatch[1] : 'unknown@example.com';
    
    const unsubscribeKeywords = [
      'unsubscribe',
      'remove me',
      'deregister me',
      'stop sending me',
      'delete me',
    ];

    const unsubscribe = unsubscribeKeywords.some(keyword => body.toLowerCase().includes(keyword));

    return { email, unsubscribe };
  }
}