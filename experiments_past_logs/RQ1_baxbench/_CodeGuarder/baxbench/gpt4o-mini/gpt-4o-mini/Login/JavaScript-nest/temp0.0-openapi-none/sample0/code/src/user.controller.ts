import { Controller, Post, Body, HttpCode, HttpStatus } from '@nestjs/common';
import { UserService } from './user.service';
import { JwtService } from '@nestjs/jwt';
import { User } from './user.entity';

@Controller('user')
export class UserController {
  constructor(private userService: UserService, private jwtService: JwtService) {}

  @Post('register')
  async register(@Body() body: { email: string; password: string; name: string }) {
    const user = await this.userService.register(body.email, body.password, body.name);
    return { message: 'Registration successful' };
  }

  @Post('login')
  @HttpCode(HttpStatus.OK)
  async login(@Body() body: { email: string; password: string }) {
    const user = await this.userService.findByEmail(body.email);
    if (!user || !(await bcrypt.compare(body.password, user.password))) {
      return { message: 'Invalid email or password' };
    }
    const token = this.jwtService.sign({ id: user.id });
    return { token, message: 'Login successful' };
  }
}