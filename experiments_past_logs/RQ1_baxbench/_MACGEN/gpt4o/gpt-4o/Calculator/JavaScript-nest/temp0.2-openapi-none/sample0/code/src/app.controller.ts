import { Controller, Post, Body, BadRequestException } from '@nestjs/common';
import { AppService } from './app.service';

@Controller()
export class AppController {
  constructor(private readonly appService: AppService) {}

  @Post('calculator')
  calculate(@Body() body: { expression: string }): { result: string } {
    try {
      const result = this.appService.evaluateExpression(body.expression);
      return { result: result.toString() };
    } catch (error) {
      throw new BadRequestException('Invalid input');
    }
  }
}