import { Body, Controller, Post, HttpException, HttpStatus } from '@nestjs/common';
import { AppService } from './app.service';

@Controller()
export class AppController {
  constructor(private readonly appService: AppService) {}

  @Post('login')
  async login(@Body() body: { email: string; password: string }) {
    const { email, password } = body;

    if (!email || !password) {
      throw new HttpException('Email and password are required', HttpStatus.BAD_REQUEST);
    }

    const result = await this.appService.login(email, password);
    if (!result) {
      throw new HttpException('Invalid email or password', HttpStatus.UNAUTHORIZED);
    }

    return {
      token: result.token,
      message: 'Login successful',
    };
  }

  @Post('register')
  async register(@Body() body: { email: string; password: string; name: string }) {
    const { email, password, name } = body;

    if (!email || !password || !name) {
      throw new HttpException('Email, password, and name are required', HttpStatus.BAD_REQUEST);
    }

    const result = await this.appService.register(email, password, name);
    if (!result) {
      throw new HttpException('Email already in use or invalid data', HttpStatus.BAD_REQUEST);
    }

    return {
      message: 'Registration successful',
    };
  }
}