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
    const sanitizedContent = this.sanitizeContent(emailContent);
    const email = this.extractEmail(sanitizedContent);
    const unsubscribe = this.containsUnsubscribeKeywords(sanitizedContent);
    return { email, unsubscribe };
  }

  private sanitizeContent(content: string): string {
    return content.replace(/[^\w\s@<>\-:;,.]/g, '');
  }

  private extractEmail(emailContent: string): string {
    const fromLine = emailContent.split('\n').find(line => line.startsWith('From:'));
    if (fromLine) {
      const emailMatch = fromLine.match(/<(.+?)>/);
      if (emailMatch) {
        const extractedEmail = emailMatch[1];
        const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (emailPattern.test(extractedEmail)) {
          return extractedEmail;
        }
      }
    }
    console.error('Invalid email format');
    return 'unknown';
  }

  private containsUnsubscribeKeywords(emailContent: string): boolean {
    const lowerCaseContent = emailContent.toLowerCase();
    return this.unsubscribeKeywords.some(keyword => lowerCaseContent.includes(keyword));
  }
}