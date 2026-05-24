import { Controller, Post, Body, Get, Query } from '@nestjs/common';
import { AppService } from './app.service';

@Controller()
export class AppController {
  constructor(private readonly appService: AppService) {}

  @Post('register')
  async register(@Body() body: { email: string; username: string; password: string }) {
    return this.appService.register(body.email, body.username, body.password);
  }

  @Post('login')
  async login(@Body() body: { email: string; password: string }) {
    return this.appService.login(body.email, body.password);
  }

  @Post('set_secret')
  async setSecret(@Body() body: { username: string; secret: string }) {
    return this.appService.setSecret(body.username, body.secret);
  }

  @Get('get_secret')
  async getSecret(@Query('username') username: string) {
    return this.appService.getSecret(username);
  }
}