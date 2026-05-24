import { Controller, Post, Body, Get, Query, Res, HttpStatus, Req } from '@nestjs/common';
import { AppService } from './app.service';
import { Response, Request } from 'express';

@Controller()
export class AppController {
  constructor(private readonly appService: AppService) {}

  @Post('merchants/register')
  async registerMerchant(@Body() body: any, @Res() res: Response) {
    const { email, name, password } = body;
    if (!email || !name || !password) {
      return res.status(HttpStatus.BAD_REQUEST).send('Invalid input');
    }
    const result = await this.appService.registerMerchant(email, name, password);
    if (result) {
      return res.status(HttpStatus.CREATED).send('Merchant registered successfully');
    }
    return res.status(HttpStatus.BAD_REQUEST).send('Invalid input');
  }

  @Post('merchants/login')
  async loginMerchant(@Body() body: any, @Res() res: Response) {
    const { email, password } = body;
    const result = await this.appService.loginMerchant(email, password);
    if (result) {
      res.cookie('AUTH_COOKIE', result, { httpOnly: true });
      return res.status(HttpStatus.OK).json('Login successful');
    }
    return res.status(HttpStatus.UNAUTHORIZED).json({ error: 'Invalid email or password' });
  }

  @Post('merchants/upload-wares')
  async uploadWares(@Body() body: any, @Req() req: Request, @Res() res: Response) {
    const { csv } = body;
    const authCookie = req.cookies['AUTH_COOKIE'];
    if (!authCookie) {
      return res.status(HttpStatus.UNAUTHORIZED).send('Unauthorized');
    }
    const result = await this.appService.uploadWares(authCookie, csv);
    if (result) {
      return res.status(HttpStatus.OK).send('Wares uploaded successfully');
    }
    return res.status(HttpStatus.BAD_REQUEST).send('Invalid CSV format');
  }

  @Get('wares')
  async getWares(@Query('minPrice') minPrice: number, @Query('maxPrice') maxPrice: number, @Res() res: Response) {
    const wares = await this.appService.getWares(minPrice, maxPrice);
    return res.status(HttpStatus.OK).send(wares);
  }
}