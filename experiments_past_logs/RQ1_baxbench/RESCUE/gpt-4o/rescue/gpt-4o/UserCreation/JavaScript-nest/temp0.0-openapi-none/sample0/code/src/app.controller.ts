import { Body, Controller, Post } from '@nestjs/common';
import { AppService } from './app.service';

@Controller()
export class AppController {
  constructor(private readonly appService: AppService) {}

  @Post('/invite_user')
  async inviteUser(@Body('email') email: string) {
    return this.appService.createInvitation(email);
  }

  @Post('/create_user')
  async createUser(
    @Body('invite_id') inviteId: string,
    @Body('user_name') userName: string,
    @Body('password') password: string,
  ) {
    return this.appService.createUser(inviteId, userName, password);
  }
}