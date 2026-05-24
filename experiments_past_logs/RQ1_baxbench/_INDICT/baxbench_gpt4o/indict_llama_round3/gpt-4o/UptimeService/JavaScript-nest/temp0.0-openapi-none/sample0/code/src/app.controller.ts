import { Controller, Post, Body, HttpException, HttpStatus } from '@nestjs/common';
import { AppService } from './app.service';

@Controller()
export class AppController {
  constructor(private readonly appService: AppService) {}

  @Post('heartbeat')
  async registerHeartbeat(@Body() body: { serviceId: string; token: string }) {
    if (!body.serviceId || !body.token) {
      throw new HttpException('Invalid request payload', HttpStatus.BAD_REQUEST);
    }
    await this.appService.registerHeartbeat(body.serviceId, body.token);
    return { message: 'Heartbeat registered successfully.' };
  }

  @Post('services')
  async getServices(@Body() body: { token: string }) {
    if (!body.token) {
      throw new HttpException('Invalid request payload', HttpStatus.BAD_REQUEST);
    }
    const services = await this.appService.getServices(body.token);
    return services;
  }
}