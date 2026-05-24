import { Controller, Post, Get, Query, Body, HttpCode, HttpStatus } from '@nestjs/common';
import { AppService } from './app.service';
import { Click } from './click.model';

@Controller('click')
export class AppController {
  constructor(private readonly appService: AppService) {}

  @Post()
  @HttpCode(HttpStatus.CREATED)
  async registerClick(@Body() click: Click) {
    return this.appService.registerClick(click);
  }

  @Get('clicks')
  async getClicks(
    @Query('date') date: string,
    @Query('direction') direction: string,
  ) {
    return this.appService.getClicks(date, direction);
  }
}