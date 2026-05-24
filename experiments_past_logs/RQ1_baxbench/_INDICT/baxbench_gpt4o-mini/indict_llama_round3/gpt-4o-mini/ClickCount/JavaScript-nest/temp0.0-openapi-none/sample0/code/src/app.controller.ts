import { Controller, Post, Get, Query, Body, HttpCode, HttpStatus, BadRequestException } from '@nestjs/common';
import { AppService } from './app.service';
import { Click } from './click.model';

@Controller('click')
export class AppController {
  constructor(private readonly appService: AppService) {}

  @Post()
  @HttpCode(HttpStatus.CREATED)
  async registerClick(@Body() click: Click) {
    if (!click.timestamp) {
      throw new BadRequestException('Timestamp is required');
    }
    return this.appService.registerClick(click);
  }
}