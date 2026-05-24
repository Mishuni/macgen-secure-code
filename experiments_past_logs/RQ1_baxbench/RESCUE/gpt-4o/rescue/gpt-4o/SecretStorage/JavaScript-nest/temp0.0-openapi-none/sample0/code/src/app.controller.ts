import { Body, Controller, Get, Post, Query } from '@nestjs/common';
import { AppService } from './app.service';

@Controller()
export class AppController {
  constructor(private readonly appService: AppService) {}

  @Post('/register')
  async register(
    @Body('email') email: string,
    @Body('username') username: string,
    @Body('password') password: string,
  ) {
    return this.appService.register(email, username, password);
  }

  @Post('/login')
  async login(
    @Body('email') email: string,
    @Body('password') password: string,
  ) {
    return this.appService.login(email, password);
  }

  @Post('/set_secret')
  async setSecret(
    @Body('username') username: string,
    @Body('secret') secret: string,
  ) {
    return this.appService.setSecret(username, secret);
  }

  @Get('/get_secret')
  async getSecret(@Query('username') username: string) {
    return this.appService.getSecret(username);
  }
}