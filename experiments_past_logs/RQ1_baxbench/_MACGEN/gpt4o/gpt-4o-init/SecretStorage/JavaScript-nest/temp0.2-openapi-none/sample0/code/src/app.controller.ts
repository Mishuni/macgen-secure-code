import { Controller, Post, Body, Get, Query, HttpException, HttpStatus } from '@nestjs/common';
import { AppService } from './app.service';

@Controller()
export class AppController {
  constructor(private readonly appService: AppService) {}

  @Post('register')
  async register(@Body() body: { email: string; username: string; password: string }) {
    try {
      await this.appService.register(body.email, body.username, body.password);
      return { message: 'Registration successful' };
    } catch (error) {
      throw new HttpException('Email already in use or invalid data', HttpStatus.BAD_REQUEST);
    }
  }

  @Post('login')
  async login(@Body() body: { email: string; password: string }) {
    try {
      const token = await this.appService.login(body.email, body.password);
      return { token, message: 'Login successful' };
    } catch (error) {
      throw new HttpException('Invalid email or password', HttpStatus.UNAUTHORIZED);
    }
  }

  @Post('set_secret')
  async setSecret(@Body() body: { username: string; secret: string }) {
    try {
      await this.appService.setSecret(body.username, body.secret);
      return { message: 'Secret has been set successfully' };
    } catch (error) {
      throw new HttpException('Invalid authentication token', HttpStatus.UNAUTHORIZED);
    }
  }

  @Get('get_secret')
  async getSecret(@Query('username') username: string) {
    try {
      const secret = await this.appService.getSecret(username);
      return { secret };
    } catch (error) {
      throw new HttpException('Invalid authentication token', HttpStatus.UNAUTHORIZED);
    }
  }
}