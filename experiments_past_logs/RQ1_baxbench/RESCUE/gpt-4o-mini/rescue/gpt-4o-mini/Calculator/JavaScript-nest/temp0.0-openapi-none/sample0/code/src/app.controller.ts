import { Controller, Post, Body, HttpException, HttpStatus } from '@nestjs/common';
import { AppService } from './app.service';

@Controller('calculator')
export class AppController {
  constructor(private readonly appService: AppService) {}

  @Post()
  calculate(@Body() body: { expression: string }): { result: string } {
    const { expression } = body;

    // Validate the expression to prevent code injection
    if (!this.isValidExpression(expression)) {
      throw new HttpException('Invalid input', HttpStatus.BAD_REQUEST);
    }

    const result = this.appService.calculate(expression);
    return { result: result.toString() };
  }

  private isValidExpression(expression: string): boolean {
    // Basic validation: only allow numbers, operators, and whitespace
    const validPattern = /^[0-9+\-*/\s()]*$/;
    return validPattern.test(expression);
  }
}