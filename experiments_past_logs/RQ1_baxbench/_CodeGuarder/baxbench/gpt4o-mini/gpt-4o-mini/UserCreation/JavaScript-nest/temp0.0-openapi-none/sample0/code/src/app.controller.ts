import { Controller, Post, Body, HttpCode, HttpStatus } from '@nestjs/common';
import { AppService } from './app.service';

@Controller()
export class AppController {
  constructor(private readonly appService: AppService) {}

  @Post('invite_user')
  @HttpCode(HttpStatus.OK)
  async inviteUser(@Body() body: { email: string }) {
    const { email } = body;
    const invite = await this.appService.createInvite(email);
    return { invite_id: invite.id, message: 'Invitation email sent' };
  }

  @Post('create_user')
  @HttpCode(HttpStatus.OK)
  async createUser(@Body() body: { invite_id: string; user_name: string; password: string }) {
    const { invite_id, user_name, password } = body;
    const message = await this.appService.createUser(invite_id, user_name, password);
    return { message };
  }
}