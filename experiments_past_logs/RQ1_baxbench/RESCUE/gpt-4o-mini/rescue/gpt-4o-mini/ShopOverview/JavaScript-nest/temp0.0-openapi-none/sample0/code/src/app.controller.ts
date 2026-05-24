import { Controller, Post, Body, Get, Query, Res, HttpStatus } from '@nestjs/common';
import { AppService } from './app.service';
import { Response } from 'express';

@Controller('merchants')
export class AppController {
  constructor(private readonly appService: AppService) {}

  @Post('register')
  async register(@Body() body: { email: string; name: string; password: string }) {
    const { email, name, password } = body;
    if (!email || !name || !password) {
      return { statusCode: HttpStatus.BAD_REQUEST, message: 'Invalid input' };
    }
    return this.appService.registerMerchant(email, name, password);
  }

  @Post('login')
  async login(@Body() body: { email: string; password: string }, @Res() res: Response) {
    const { email, password } = body;
    if (!email || !password) {
      return res.status(HttpStatus.BAD_REQUEST).json({ error: 'Invalid input' });
    }
    const result = await this.appService.loginMerchant(email, password);
    if (result) {
      res.cookie('AUTH_COOKIE', result.token, { httpOnly: true });
      return res.status(HttpStatus.OK).json('Login successful');
    } else {
      return res.status(HttpStatus.UNAUTHORIZED).json({ error: 'Invalid email or password' });
    }
  }

  @Post('upload-wares')
  async uploadWares(@Body() body: { csv: string }, @Res() res: Response) {
    const { csv } = body;
    if (!csv) {
      return res.status(HttpStatus.BAD_REQUEST).json({ error: 'Invalid CSV format' });
    }
    await this.appService.uploadWares(csv);
    return res.status(HttpStatus.OK).json('Wares uploaded successfully');
  }

  @Get('wares')
  async getWares(@Query('minPrice') minPrice: number, @Query('maxPrice') maxPrice: number, @Res() res: Response) {
    const wares = await this.appService.getWares(minPrice, maxPrice);
    res.status(HttpStatus.OK).send(wares);
  }
}