import { Controller, Post, Body, HttpException, HttpStatus } from '@nestjs/common';
import { AppService } from './app.service';

@Controller('calculator')
export class AppController {
  constructor(private readonly appService: AppService) {}

  @Post()
  calculate(@Body() body: { expression: string }) {
    const { expression } = body;

    if (typeof expression !== 'string' || !this.isValidExpression(expression)) {
      throw new HttpException('Invalid input', HttpStatus.BAD_REQUEST);
    }

    const result = this.appService.evaluateExpression(expression);
    return { result: result.toString() };
  }

  private isValidExpression(expression: string): boolean {
    const safePattern = /^[\d\s+*/()-]+$/; // Allow only digits, spaces, and basic operators
    return safePattern.test(expression);
  }
}