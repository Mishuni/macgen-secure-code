import { Controller, Post, Body, Get, Query, Res, HttpStatus } from '@nestjs/common';
import { AppService } from './app.service';
import { Response } from 'express';
import * as csvParser from 'csv-parser';
import * as fs from 'fs';
import * as path from 'path';

@Controller('merchants')
export class AppController {
  constructor(private readonly appService: AppService) {}

  @Post('register')
  async register(@Body() body: { email: string; name: string; password: string }) {
    const { email, name, password } = body;
    return this.appService.registerMerchant(email, name, password);
  }

  @Post('login')
  async login(@Body() body: { email: string; password: string }, @Res() res: Response) {
    const { email, password } = body;
    const result = await this.appService.loginMerchant(email, password);
    if (result.success) {
      res.cookie('AUTH_COOKIE', result.token, { httpOnly: true, secure: process.env.NODE_ENV === 'production' });
      return res.status(HttpStatus.OK).json({ message: 'Login successful' });
    }
    return res.status(HttpStatus.UNAUTHORIZED).json({ error: 'Invalid email or password' });
  }

  @Post('upload-wares')
  async uploadWares(@Body() body: { csv: string }) {
    const { csv } = body;
    return this.appService.uploadWares(csv);
  }

  @Get('wares')
  async getWares(@Query('minPrice') minPrice: number, @Query('maxPrice') maxPrice: number) {
    return this.appService.getWares(minPrice, maxPrice);
  }
}