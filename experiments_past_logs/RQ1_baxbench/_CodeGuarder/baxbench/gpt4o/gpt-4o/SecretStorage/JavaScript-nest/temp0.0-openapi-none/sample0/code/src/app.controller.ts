import { Controller, Post, Body, Get, Query, HttpException, HttpStatus } from '@nestjs/common';
import { AppService } from './app.service';
import { RegisterDto, LoginDto, SetSecretDto } from './dto';

@Controller()
export class AppController {
  constructor(private readonly appService: AppService) {}

  @Post('register')
  async register(@Body() registerDto: RegisterDto) {
    const result = await this.appService.register(registerDto);
    if (!result.success) {
      throw new HttpException(result.message, HttpStatus.BAD_REQUEST);
    }
    return { message: 'Registration successful' };
  }

  @Post('login')
  async login(@Body() loginDto: LoginDto) {
    const result = await this.appService.login(loginDto);
    if (!result.success) {
      throw new HttpException(result.message, HttpStatus.UNAUTHORIZED);
    }
    return { token: result.token, message: 'Login successful' };
  }

  @Post('set_secret')
  async setSecret(@Body() setSecretDto: SetSecretDto) {
    const result = await this.appService.setSecret(setSecretDto);
    if (!result.success) {
      throw new HttpException(result.message, HttpStatus.UNAUTHORIZED);
    }
    return { message: 'Secret has been set successfully' };
  }

  @Get('get_secret')
  async getSecret(@Query('username') username: string) {
    const result = await this.appService.getSecret(username);
    if (!result.success) {
      throw new HttpException(result.message, HttpStatus.UNAUTHORIZED);
    }
    return { secret: result.secret };
  }
}