import { Controller, Get, Post, Body, Query, Res, HttpStatus } from '@nestjs/common';
import { AppService } from './app.service';
import { Response } from 'express';

@Controller()
export class AppController {
  constructor(private readonly appService: AppService) {}

  @Get()
  getHello(): string {
    return this.appService.getHello();
  }

  @Post('merchants/register')
  async registerMerchant(@Body() body: { email: string; name: string; password: string }, @Res() res: Response) {
    try {
      const result = await this.appService.registerMerchant(body);
      return res.status(HttpStatus.CREATED).json(result);
    } catch (error) {
      return res.status(HttpStatus.BAD_REQUEST).json({ error: error.message });
    }
  }

  @Post('merchants/login')
  async loginMerchant(@Body() body: { email: string; password: string }, @Res() res: Response) {
    const result = await this.appService.loginMerchant(body);
    if (result.success) {
      res.cookie('AUTH_COOKIE', result.token);
      return res.status(HttpStatus.OK).json({ message: 'Login successful' });
    }
    return res.status(HttpStatus.UNAUTHORIZED).json({ error: 'Invalid email or password' });
  }

  @Post('merchants/upload-wares')
  async uploadWares(@Body() body: { csv: string }, @Res() res: Response) {
    try {
      const result = await this.appService.uploadWares(body.csv);
      return res.status(HttpStatus.OK).json(result);
    } catch (error) {
      return res.status(HttpStatus.BAD_REQUEST).json({ error: error.message });
    }
  }

  @Get('wares')
  async getWares(@Query('minPrice') minPrice: number, @Query('maxPrice') maxPrice: number, @Res() res: Response) {
    const wares = await this.appService.getWares(minPrice, maxPrice);
    return res.status(HttpStatus.OK).send(wares);
  }
}