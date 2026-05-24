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

  shouldUnsubscribe(emailContent: string): boolean {
    const lowerCaseContent = emailContent.toLowerCase();
    return this.unsubscribeKeywords.some(keyword => lowerCaseContent.includes(keyword));
  }
}