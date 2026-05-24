import { Controller, Post, Body } from '@nestjs/common';
import { AppService } from './app.service';

@Controller()
export class AppController {
  constructor(private readonly appService: AppService) {}

  @Post('/decideUnsubscribe')
  decideUnsubscribe(@Body() emailContent: string): { email: string; unsubscribe: boolean } {
    const email = this.extractEmail(emailContent);
    const unsubscribe = this.appService.shouldUnsubscribe(emailContent);
    return { email, unsubscribe };
  }

  private extractEmail(emailContent: string): string {
    const emailMatch = emailContent.match(/From:\s*.*<(.+?)>/);
    return emailMatch ? emailMatch[1] : 'unknown@example.com';
  }
}