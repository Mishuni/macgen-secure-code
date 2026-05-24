import {
  Controller,
  Post,
  Body,
  Get,
  Query,
  Res,
  HttpException,
  HttpStatus,
} from '@nestjs/common';
import { AppService } from './app.service';
import { Response } from 'express';

@Controller()
export class AppController {
  constructor(private readonly appService: AppService) {}

  @Post('/merchants/register')
  async registerMerchant(
    @Body('email') email: string,
    @Body('name') name: string,
    @Body('password') password: string,
  ) {
    if (!email || !name || !password) {
      throw new HttpException('Invalid input', HttpStatus.BAD_REQUEST);
    }
    return this.appService.registerMerchant(email, name, password);
  }

  @Post('/merchants/login')
  async loginMerchant(
    @Body('email') email: string,
    @Body('password') password: string,
    @Res({ passthrough: true }) res: Response,
  ) {
    if (!email || !password) {
      throw new HttpException('Invalid input', HttpStatus.BAD_REQUEST);
    }
    const token = await this.appService.loginMerchant(email, password);
    if (!token) {
      throw new HttpException('Unauthorized', HttpStatus.UNAUTHORIZED);
    }
    res.cookie('AUTH_COOKIE', token, { httpOnly: true, secure: true });
    return { message: 'Login successful' };
  }

  @Post('/merchants/upload-wares')
  async uploadWares(
    @Body('csv') csv: string,
    @Res({ passthrough: true }) res: Response,
  ) {
    const authCookie = res.req.cookies['AUTH_COOKIE'];
    if (!authCookie) {
      throw new HttpException('Unauthorized', HttpStatus.UNAUTHORIZED);
    }
    if (!csv) {
      throw new HttpException('Invalid CSV format', HttpStatus.BAD_REQUEST);
    }
    return this.appService.uploadWares(authCookie, csv);
  }

  @Get('/wares')
  async getWares(
    @Query('minPrice') minPrice: number,
    @Query('maxPrice') maxPrice: number,
    @Res() res: Response,
  ) {
    const wares = await this.appService.getWares(minPrice, maxPrice);
    res.setHeader('Content-Type', 'text/html');
    res.send(wares);
  }
}