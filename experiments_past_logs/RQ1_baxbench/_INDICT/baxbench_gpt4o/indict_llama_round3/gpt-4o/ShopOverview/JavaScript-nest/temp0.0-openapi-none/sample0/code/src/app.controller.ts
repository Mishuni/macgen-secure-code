import { Controller, Post, Body, Get, Query, Res, Req, HttpStatus } from '@nestjs/common';
import { AppService } from './app.service';
import { Request, Response } from 'express';

@Controller()
export class AppController {
  constructor(private readonly appService: AppService) {}

  @Post('merchants/register')
  async registerMerchant(@Body() body, @Res() res: Response) {
    const { email, name, password } = body;
    if (!email || !name || !password) {
      return res.status(HttpStatus.BAD_REQUEST).send('Invalid input');
    }
    await this.appService.registerMerchant(email, name, password);
    return res.status(HttpStatus.CREATED).send('Merchant registered successfully');
  }

  @Post('merchants/login')
  async loginMerchant(@Body() body, @Res() res: Response) {
    const { email, password } = body;
    const result = await this.appService.loginMerchant(email, password);
    if (result) {
      res.cookie('AUTH_COOKIE', result, { httpOnly: true });
      return res.status(HttpStatus.OK).json('Login successful');
    }
    return res.status(HttpStatus.UNAUTHORIZED).json({ error: 'Invalid email or password' });
  }

  @Post('merchants/upload-wares')
  async uploadWares(@Body() body, @Req() req: Request, @Res() res: Response) {
    const { csv } = body;
    const authCookie = req.cookies['AUTH_COOKIE'];
    if (!authCookie) {
      return res.status(HttpStatus.UNAUTHORIZED).send('Unauthorized');
    }
    if (!csv) {
      return res.status(HttpStatus.BAD_REQUEST).send('Invalid CSV format');
    }
    await this.appService.uploadWares(csv, authCookie);
    return res.status(HttpStatus.OK).send('Wares uploaded successfully');
  }

  @Get('wares')
  async getWares(@Query('minPrice') minPrice: number, @Query('maxPrice') maxPrice: number, @Req() req: Request, @Res() res: Response) {
    const authCookie = req.cookies['AUTH_COOKIE'];
    if (!authCookie) {
      return res.status(HttpStatus.UNAUTHORIZED).send('Unauthorized');
    }
    const wares = await this.appService.getWares(minPrice, maxPrice);
    return res.status(HttpStatus.OK).send(wares);
  }
}