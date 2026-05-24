import { Body, Controller, Post, HttpException, HttpStatus } from '@nestjs/common';
import { AppService } from './app.service';

@Controller()
export class AppController {
  constructor(private readonly appService: AppService) {}

  @Post('login')
  async login(@Body() body: { email: string; password: string }) {
    const result = await this.appService.login(body.email, body.password);
    if (!result) {
      throw new HttpException('Invalid email or password', HttpStatus.UNAUTHORIZED);
    }
    return result;
  }

  @Post('register')
  async register(@Body() body: { email: string; password: string; name: string }) {
    const result = await this.appService.register(body.email, body.password, body.name);
    if (!result) {
      throw new HttpException('Email already in use or invalid data', HttpStatus.BAD_REQUEST);
    }
    return result;
  }
}