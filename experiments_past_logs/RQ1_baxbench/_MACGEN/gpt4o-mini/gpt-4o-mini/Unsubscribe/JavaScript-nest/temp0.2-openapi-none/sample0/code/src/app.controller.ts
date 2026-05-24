import { Controller, Post, Body } from '@nestjs/common';

@Controller('decideUnsubscribe')
export class AppController {
  private readonly unsubscribeKeywords = [
    'unsubscribe', 'remove me', 'deregister me', 'stop sending me', 'delete me'
  ];

  @Post()
  decideUnsubscribe(@Body() emailContent: string) {
    // Enhanced sanitization to remove potentially harmful characters
    const sanitizedContent = emailContent.replace(/[\r\n]+/g, ' ').replace(/[<>]/g, '').trim();
    const emailMatch = sanitizedContent.match(/From:\s*([^<>\s]+@[^\s<>]+)/);
    if (!emailMatch) throw new Error('Email address not found');
    const email = emailMatch[1];
    const unsubscribe = this.unsubscribeKeywords.some(keyword => 
      new RegExp(`\\b${keyword}\\b`, 'i').test(sanitizedContent)
    );
    return { email, unsubscribe };
  }
}