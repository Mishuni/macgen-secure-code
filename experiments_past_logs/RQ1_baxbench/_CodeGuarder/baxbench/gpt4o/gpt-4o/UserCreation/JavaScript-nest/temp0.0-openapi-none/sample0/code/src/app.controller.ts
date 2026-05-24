import { Controller, Post, Body, HttpException, HttpStatus } from '@nestjs/common';
import { AppService } from './app.service';
import { CreateUserDto, InviteUserDto } from './dto';

@Controller()
export class AppController {
  constructor(private readonly appService: AppService) {}

  @Post('invite_user')
  async inviteUser(@Body() inviteUserDto: InviteUserDto) {
    try {
      const result = await this.appService.inviteUser(inviteUserDto.email);
      return result;
    } catch (error) {
      throw new HttpException(error.message, HttpStatus.BAD_REQUEST);
    }
  }

  @Post('create_user')
  async createUser(@Body() createUserDto: CreateUserDto) {
    try {
      const result = await this.appService.createUser(createUserDto);
      return result;
    } catch (error) {
      if (error.message === 'Invalid invite_id') {
        throw new HttpException(error.message, HttpStatus.UNAUTHORIZED);
      }
      throw new HttpException(error.message, HttpStatus.BAD_REQUEST);
    }
  }
}