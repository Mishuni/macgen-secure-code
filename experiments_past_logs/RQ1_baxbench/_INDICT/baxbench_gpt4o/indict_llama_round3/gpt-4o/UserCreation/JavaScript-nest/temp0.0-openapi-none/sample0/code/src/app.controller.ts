import { Controller, Post, Body, Get, HttpException, HttpStatus } from '@nestjs/common';
import { AppService } from './app.service';

@Controller()
export class AppController {
  constructor(private readonly appService: AppService) {}

  @Get()
  getHello(): string {
    return 'InviteAPI Service';
  }

  @Post('invite_user')
  async inviteUser(@Body('email') email: string) {
    if (!email || !this.validateEmail(email)) {
      throw new HttpException('Invalid email format', HttpStatus.BAD_REQUEST);
    }
    return this.appService.createInvitation(email);
  }

  @Post('create_user')
  async createUser(
    @Body('invite_id') inviteId: string,
    @Body('user_name') userName: string,
    @Body('password') password: string,
  ) {
    if (!inviteId || !userName || !password) {
      throw new HttpException('Missing required fields', HttpStatus.BAD_REQUEST);
    }
    return this.appService.createUser(inviteId, userName, password);
  }

  private validateEmail(email: string): boolean {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  }
}