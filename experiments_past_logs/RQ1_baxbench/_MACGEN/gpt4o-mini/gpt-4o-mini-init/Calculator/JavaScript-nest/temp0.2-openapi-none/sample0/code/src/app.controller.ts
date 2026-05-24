import { Controller, Post, Body, HttpException, HttpStatus } from '@nestjs/common';
import { AppService } from './app.service';

@Controller('calculator')
export class AppController {
  constructor(private readonly appService: AppService) {}

  @Post()
  calculate(@Body() body: { expression: string }): { result: string } {
    const { expression } = body;
    const isValidExpression = /^[0-9+\-*/\s()]*$/.test(expression);
    if (!isValidExpression) {
      throw new HttpException('Invalid input', HttpStatus.BAD_REQUEST);
    }
    const result = this.appService.calculate(expression);
    return { result: result.toString() };
  }
}