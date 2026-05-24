import { Controller, Post, Body, HttpCode, HttpStatus } from '@nestjs/common';

@Controller('decideUnsubscribe')
export class AppController {
  @Post()
  @HttpCode(HttpStatus.OK)
  decideUnsubscribe(@Body() body: string): { email: string; unsubscribe: boolean } {
    const email = this.extractEmail(body);
    const unsubscribe = this.checkUnsubscribeRequest(body);
    return { email, unsubscribe };
  }

  private extractEmail(body: string): string {
    const emailRegex = /From:\s*([^<>\s]+<([^<>\s]+)>|([^<>\s]+))/;
    const match = body.match(emailRegex);
    return match ? match[2] || match[1] : '';
  }

  private checkUnsubscribeRequest(body: string): boolean {
    const unsubscribeKeywords = [
      'unsubscribe',
      'remove me',
      'deregister me',
      'stop sending me',
      'delete me',
    ];
    return unsubscribeKeywords.some(keyword => body.toLowerCase().includes(keyword));
  }
}