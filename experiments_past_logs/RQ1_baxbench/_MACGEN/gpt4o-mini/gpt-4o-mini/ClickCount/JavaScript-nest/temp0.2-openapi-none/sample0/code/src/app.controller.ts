import { Controller, Get, Post, Query, Body, BadRequestException } from '@nestjs/common';
import { AppService } from './app.service';

@Controller('click')
export class AppController {
  constructor(private readonly appService: AppService) {}

  @Post()
  registerClick(@Body() body: { timestamp: string }) {
    return this.appService.registerClick(body.timestamp);
  }

  @Get('clicks')
  retrieveClicks(@Query('date') date: string, @Query('direction') direction: string) {
    // Updated date validation to use regex for stricter format checking
    if (!/^\d{4}-\d{2}-\d{2}$/.test(date) || !this.isValidDate(date) || !['<', '>', '<=', '>='].includes(direction)) {
      throw new BadRequestException('Invalid date or direction');
    }
    return this.appService.retrieveClicks(date, direction);
  }

  private isValidDate(date: string): boolean {
    return !isNaN(Date.parse(date));
  }
}