import { Controller, Post, Body, Get, Query, Res, HttpStatus, UseGuards } from '@nestjs/common';
import { AppService } from './app.service';
import { Response } from 'express';
import { AuthGuard } from './auth.guard';

@Controller()
export class AppController {
  constructor(private readonly appService: AppService) {}

  @Post('merchants/register')
  async registerMerchant(@Body() body: any, @Res() res: Response) {
    const { email, name, password } = body;
    if (!email || !name || !password) {
      return res.status(HttpStatus.BAD_REQUEST).json({ error: 'Invalid input' });
    }
    await this.appService.registerMerchant(email, name, password);
    return res.status(HttpStatus.CREATED).json({ message: 'Merchant registered successfully' });
  }

  @Post('merchants/login')
  async loginMerchant(@Body() body: any, @Res() res: Response) {
    const { email, password } = body;
    if (!email || !password) {
      return res.status(HttpStatus.BAD_REQUEST).json({ error: 'Invalid input' });
    }
    const token = await this.appService.loginMerchant(email, password);
    if (!token) {
      return res.status(HttpStatus.UNAUTHORIZED).json({ error: 'Invalid email or password' });
    }
    res.cookie('AUTH_COOKIE', token, { httpOnly: true, secure: true });
    return res.status(HttpStatus.OK).json({ message: 'Login successful' });
  }

  @Post('merchants/upload-wares')
  @UseGuards(AuthGuard)
  async uploadWares(@Body() body: any, @Res() res: Response) {
    const { csv } = body;
    if (!csv) {
      return res.status(HttpStatus.BAD_REQUEST).json({ error: 'Invalid CSV format' });
    }
    await this.appService.uploadWares(csv);
    return res.status(HttpStatus.OK).json({ message: 'Wares uploaded successfully' });
  }

  @Get('wares')
  @UseGuards(AuthGuard)
  async getWares(@Query('minPrice') minPrice: number, @Query('maxPrice') maxPrice: number, @Res() res: Response) {
    const wares = await this.appService.getWares(minPrice, maxPrice);
    return res.status(HttpStatus.OK).send(wares);
  }
}