import { Controller, Post, Body } from '@nestjs/common';
import { AppService } from './app.service';

@Controller()
export class AppController {
  constructor(private readonly appService: AppService) {}

  @Post('invite_user')
  async inviteUser(@Body() body: { email: string }) {
    return this.appService.inviteUser(body.email);
  }

  @Post('create_user')
  async createUser(@Body() body: { invite_id: string; user_name: string; password: string }) {
    return this.appService.createUser(body.invite_id, body.user_name, body.password);
  }
}