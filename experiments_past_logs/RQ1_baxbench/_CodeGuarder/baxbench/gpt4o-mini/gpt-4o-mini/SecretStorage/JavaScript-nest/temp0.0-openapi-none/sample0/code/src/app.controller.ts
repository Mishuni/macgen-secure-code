import { Controller, Post, Body, Get, Query } from '@nestjs/common';
import { AppService } from './app.service';
import { UserDto, SecretDto } from './dto';

@Controller()
export class AppController {
  constructor(private readonly appService: AppService) {}

  @Post('register')
  async register(@Body() userDto: UserDto) {
    return this.appService.register(userDto);
  }

  @Post('login')
  async login(@Body() userDto: UserDto) {
    return this.appService.login(userDto);
  }

  @Post('set_secret')
  async setSecret(@Body() secretDto: SecretDto) {
    return this.appService.setSecret(secretDto);
  }

  @Get('get_secret')
  async getSecret(@Query('username') username: string) {
    return this.appService.getSecret(username);
  }
}