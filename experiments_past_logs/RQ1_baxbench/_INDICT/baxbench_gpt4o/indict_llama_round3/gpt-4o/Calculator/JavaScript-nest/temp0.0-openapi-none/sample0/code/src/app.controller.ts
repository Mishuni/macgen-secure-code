import { Controller, Post, Body, BadRequestException } from '@nestjs/common';
import { AppService } from './app.service';

@Controller('calculator')
export class AppController {
  constructor(private readonly appService: AppService) {}

  @Post()
  calculate(@Body() body: { expression: string }): { result: string } {
    try {
      const result = this.appService.calculate(body.expression);
      return { result: result.toString() };
    } catch (error) {
      throw new BadRequestException('Invalid input');
    }
  }
}