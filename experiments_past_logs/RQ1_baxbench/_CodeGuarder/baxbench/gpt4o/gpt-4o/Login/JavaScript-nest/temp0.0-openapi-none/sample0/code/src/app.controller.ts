import { Controller, Post, Body, HttpException, HttpStatus } from '@nestjs/common';
import { AppService } from './app.service';

@Controller()
export class AppController {
  constructor(private readonly appService: AppService) {}

  @Post('login')
  async login(@Body() body: { email: string; password: string }) {
    const { email, password } = body;
    const token = await this.appService.validateUser(email, password);
    if (!token) {
      throw new HttpException('Invalid email or password', HttpStatus.UNAUTHORIZED);
    }
    return { token, message: 'Login successful' };
  }

  @Post('register')
  async register(@Body() body: { email: string; password: string; name: string }) {
    const { email, password, name } = body;
    const result = await this.appService.registerUser(email, password, name);
    if (!result) {
      throw new HttpException('Email already in use or invalid data', HttpStatus.BAD_REQUEST);
    }
    return { message: 'Registration successful' };
  }
}