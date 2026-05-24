import { Controller, Post, Body } from '@nestjs/common';
import { AppService } from './app.service';

@Controller()
export class AppController {
  constructor(private readonly appService: AppService) {}

  @Post('/decideUnsubscribe')
  async decideUnsubscribe(@Body() body: { email: string }): Promise<{ email: string; unsubscribe: boolean }> {
    const emailContent = body.email;

    // Validate input
    if (!emailContent || typeof emailContent !== 'string') {
      throw new Error('Invalid email content');
    }

    // Process the email content
    return this.appService.processEmail(emailContent);
  }
}