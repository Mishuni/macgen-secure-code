import { Injectable } from '@nestjs/common';

@Injectable()
export class AppService {
  private unsubscribeKeywords = [
    'unsubscribe',
    'remove me',
    'deregister me',
    'stop sending me',
    'delete me',
  ];

  decideUnsubscribe(emailContent: string): { email: string; unsubscribe: boolean } {
    const emailMatch = emailContent.match(/From:\s*.*<(.+?)>/i);
    const email = emailMatch ? emailMatch[1] : '';

    const unsubscribe = this.unsubscribeKeywords.some(keyword =>
      emailContent.toLowerCase().includes(keyword),
    );

    return { email, unsubscribe };
  }
}