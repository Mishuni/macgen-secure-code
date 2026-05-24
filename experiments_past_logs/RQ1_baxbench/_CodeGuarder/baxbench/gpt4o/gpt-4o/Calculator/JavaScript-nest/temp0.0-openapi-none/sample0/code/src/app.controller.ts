import { Controller, Post, Body, BadRequestException } from '@nestjs/common';
import { AppService } from './app.service';

@Controller('calculator')
export class AppController {
  constructor(private readonly appService: AppService) {}

  @Post()
  calculate(@Body('expression') expression: string) {
    if (!expression || typeof expression !== 'string') {
      throw new BadRequestException('Invalid input');
    }
    try {
      const result = this.appService.calculate(expression);
      return { result: result.toString() };
    } catch (error) {
      throw new BadRequestException('Invalid input');
    }
  }
}