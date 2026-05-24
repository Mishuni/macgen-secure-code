import { Controller, Post, Body, HttpException, HttpStatus } from '@nestjs/common';
import { AppService } from './app.service';

@Controller('calculator')
export class AppController {
  constructor(private readonly appService: AppService) {}

  @Post()
  calculate(@Body() body: { expression: string }): { result: string } {
    try {
      const result = this.appService.calculateExpression(body.expression);
      return { result: result.toString() };
    } catch (error) {
      throw new HttpException('Invalid input', HttpStatus.BAD_REQUEST);
    }
  }
}