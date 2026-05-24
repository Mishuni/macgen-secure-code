import { Controller, Post, Get, Body, Query } from '@nestjs/common';
import { AppService } from './app.service';
import { Click } from './click.interface';

@Controller('click')
export class AppController {
  constructor(private readonly appService: AppService) {}

  @Post()
  async registerClick(@Body() click: Click): Promise<{ message: string }> {
    await this.appService.registerClick(click);
    return { message: 'Click registered successfully' };
  }

  @Get('clicks')
  async getClicks(
    @Query('date') date: string,
    @Query('direction') direction: string,
  ): Promise<Click[]> {
    return this.appService.getClicks(date, direction);
  }
}