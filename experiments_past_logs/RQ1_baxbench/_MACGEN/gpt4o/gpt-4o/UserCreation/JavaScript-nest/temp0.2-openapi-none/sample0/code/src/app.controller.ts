import { Body, Controller, Post } from '@nestjs/common';
import { AppService } from './app.service';
import { IsEmail, IsString, Length } from 'class-validator';

class InviteUserDto {
  @IsEmail()
  email: string;
}

class CreateUserDto {
  @IsString()
  invite_id: string;

  @IsString()
  @Length(3, 20)
  user_name: string;

  @IsString()
  @Length(8, 64)
  password: string;
}

@Controller()
export class AppController {
  constructor(private readonly appService: AppService) {}

  @Post('invite_user')
  async inviteUser(@Body() body: InviteUserDto) {
    return this.appService.createInvitation(body.email);
  }

  @Post('create_user')
  async createUser(@Body() body: CreateUserDto) {
    return this.appService.createUser(body.invite_id, body.user_name, body.password);
  }
}