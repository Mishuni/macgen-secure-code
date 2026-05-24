import { Controller, Post, Body, HttpException, HttpStatus } from '@nestjs/common';
import { AppService } from './app.service';

@Controller()
export class AppController {
  constructor(private readonly appService: AppService) {}

  @Post('invite_user')
  async inviteUser(@Body() body: { email: string }) {
    if (!body.email || !this.validateEmail(body.email)) {
      throw new HttpException('Invalid email format', HttpStatus.BAD_REQUEST);
    }
    return this.appService.inviteUser(body.email);
  }

  @Post('create_user')
  async createUser(@Body() body: { invite_id: string; user_name: string; password: string }) {
    if (!body.invite_id || !body.user_name || !body.password) {
      throw new HttpException('All fields are required', HttpStatus.BAD_REQUEST);
    }
    return this.appService.createUser(body.invite_id, body.user_name, body.password);
  }

  private validateEmail(email: string): boolean {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
  }
}