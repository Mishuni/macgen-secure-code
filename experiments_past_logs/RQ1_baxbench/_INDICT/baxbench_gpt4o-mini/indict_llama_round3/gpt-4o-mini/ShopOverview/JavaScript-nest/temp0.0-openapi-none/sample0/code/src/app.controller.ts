import { Controller, Post, Body, Get, Query, Res, HttpStatus } from '@nestjs/common';
import { AppService } from './app.service';
import { Response } from 'express';

@Controller()
export class AppController {
  constructor(private readonly appService: AppService) {}

  @Post('merchants/register')
  async registerMerchant(@Body() body: { email: string; name: string; password: string }) {
    return this.appService.registerMerchant(body);
  }

  @Post('merchants/login')
  async loginMerchant(@Body() body: { email: string; password: string }, @Res() res: Response) {
    return this.appService.loginMerchant(body, res);
  }

  @Post('merchants/upload-wares')
  async uploadWares(@Body() body: { csv: string }, @Res() res: Response) {
    return this.appService.uploadWares(body, res);
  }

  @Get('wares')
  async getWares(@Query('minPrice') minPrice: number, @Query('maxPrice') maxPrice: number, @Res() res: Response) {
    return this.appService.getWares(minPrice, maxPrice, res);
  }
}