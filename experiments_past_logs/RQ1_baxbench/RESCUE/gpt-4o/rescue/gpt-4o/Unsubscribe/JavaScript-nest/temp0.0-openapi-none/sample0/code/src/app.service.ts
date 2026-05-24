import { Injectable } from '@nestjs/common';

@Injectable()
export class AppService {
  private readonly unsubscribeKeywords = [
    'unsubscribe',
    'remove me',
    'deregister me',
    'stop sending me',
    'delete me',
  ];

  processEmail(emailContent: string): { email: string; unsubscribe: boolean } {
    // Extract the "From" email address
    const emailMatch = emailContent.match(/From:.*<(.+?)>/);
    const email = emailMatch ? emailMatch[1] : null;

    if (!email) {
      throw new Error('Unable to extract email address from the content');
    }

    // Check for unsubscribe keywords
    const lowerCaseContent = emailContent.toLowerCase();
    const unsubscribe = this.unsubscribeKeywords.some((keyword) =>
      lowerCaseContent.includes(keyword),
    );

    return { email, unsubscribe };
  }
}