import { Body, Controller, Get, Post, Query, Res, HttpStatus, Headers } from '@nestjs/common';
import { AppService } from './app.service';

@Controller()
export class AppController {
  constructor(private readonly appService: AppService) {}

  @Post('register')
  async register(@Body() body, @Res() res) {
    const { email, username, password } = body;
    try {
      await this.appService.registerUser(email, username, password);
      return res.status(HttpStatus.CREATED).json({ message: 'Registration successful' });
    } catch (error) {
      return res.status(HttpStatus.BAD_REQUEST).json({ message: error.message });
    }
  }

  @Post('login')
  async login(@Body() body, @Res() res) {
    const { email, password } = body;
    try {
      const token = await this.appService.loginUser(email, password);
      return res.status(HttpStatus.OK).json({ token, message: 'Login successful' });
    } catch (error) {
      return res.status(HttpStatus.UNAUTHORIZED).json({ message: error.message });
    }
  }

  @Post('set_secret')
  async setSecret(@Body() body, @Headers('Authorization') authHeader: string, @Res() res) {
    const { username, secret } = body;
    try {
      await this.appService.setSecret(username, secret, authHeader);
      return res.status(HttpStatus.OK).json({ message: 'Secret has been set successfully' });
    } catch (error) {
      return res.status(HttpStatus.UNAUTHORIZED).json({ message: error.message });
    }
  }

  @Get('get_secret')
  async getSecret(@Query('username') username: string, @Headers('Authorization') authHeader: string, @Res() res) {
    try {
      const secret = await this.appService.getSecret(username, authHeader);
      return res.status(HttpStatus.OK).json({ secret });
    } catch (error) {
      return res.status(HttpStatus.UNAUTHORIZED).json({ message: error.message });
    }
  }
}