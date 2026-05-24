import { Body, Controller, Post, HttpException, HttpStatus } from '@nestjs/common';
import { AppService } from './app.service';

@Controller()
export class AppController {
  constructor(private readonly appService: AppService) {}

  @Post('/heartbeat')
  async registerHeartbeat(@Body() body: { serviceId: string; token: string }) {
    const { serviceId, token } = body;

    // Validate input
    if (!serviceId || !token) {
      throw new HttpException('Invalid request payload', HttpStatus.BAD_REQUEST);
    }

    try {
      await this.appService.registerHeartbeat(serviceId, token);
      return { message: 'Heartbeat registered successfully' };
    } catch (error) {
      console.error('Error registering heartbeat:', error);
      throw new HttpException('Internal server error', HttpStatus.INTERNAL_SERVER_ERROR);
    }
  }

  @Post('/services')
  async getServices(@Body() body: { token: string }) {
    const { token } = body;

    // Validate input
    if (!token) {
      throw new HttpException('Invalid request payload', HttpStatus.BAD_REQUEST);
    }

    try {
      const services = await this.appService.getServicesByToken(token);
      return services;
    } catch (error) {
      console.error('Error fetching services:', error);
      throw new HttpException('Internal server error', HttpStatus.INTERNAL_SERVER_ERROR);
    }
  }
}