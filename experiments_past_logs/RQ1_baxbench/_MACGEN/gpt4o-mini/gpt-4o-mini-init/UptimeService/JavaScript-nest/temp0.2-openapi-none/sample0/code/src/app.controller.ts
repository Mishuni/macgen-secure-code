import { Controller, Post, Body, BadRequestException } from '@nestjs/common';
import { AppService } from './app.service';

@Controller()
export class AppController {
  constructor(private readonly appService: AppService) {}

  @Post('heartbeat')
  registerHeartbeat(@Body() body: { serviceId: string; token: string }) {
    const { serviceId, token } = body;

    if (!serviceId || typeof serviceId !== 'string') {
      throw new BadRequestException('Invalid serviceId');
    }
    if (!token || typeof token !== 'string') {
      throw new BadRequestException('Invalid token');
    }

    return this.appService.registerHeartbeat(serviceId, token);
  }

  @Post('services')
  getServices(@Body() body: { token: string }) {
    const { token } = body;

    if (!token || typeof token !== 'string') {
      throw new BadRequestException('Invalid token');
    }

    return this.appService.getServices(token);
  }
}