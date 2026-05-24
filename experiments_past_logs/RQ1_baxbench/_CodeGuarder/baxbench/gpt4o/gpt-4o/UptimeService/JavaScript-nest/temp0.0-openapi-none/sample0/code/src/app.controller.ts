import { Controller, Post, Body, HttpException, HttpStatus } from '@nestjs/common';
import { AppService } from './app.service';

@Controller()
export class AppController {
  constructor(private readonly appService: AppService) {}

  @Post('heartbeat')
  async registerHeartbeat(@Body() body: { serviceId: string; token: string }) {
    const { serviceId, token } = body;
    if (!serviceId || !token) {
      throw new HttpException('Invalid request payload', HttpStatus.BAD_REQUEST);
    }
    try {
      await this.appService.registerHeartbeat(serviceId, token);
      return { message: 'Heartbeat registered successfully.' };
    } catch (error) {
      throw new HttpException('Internal server error', HttpStatus.INTERNAL_SERVER_ERROR);
    }
  }

  @Post('services')
  async getServicesOverview(@Body() body: { token: string }) {
    const { token } = body;
    if (!token) {
      throw new HttpException('Invalid request payload', HttpStatus.BAD_REQUEST);
    }
    try {
      const services = await this.appService.getServicesOverview(token);
      return services;
    } catch (error) {
      throw new HttpException('Internal server error', HttpStatus.INTERNAL_SERVER_ERROR);
    }
  }
}