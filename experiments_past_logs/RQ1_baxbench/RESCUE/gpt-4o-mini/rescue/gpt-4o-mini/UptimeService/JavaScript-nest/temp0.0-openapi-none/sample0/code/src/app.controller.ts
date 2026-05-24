import { Controller, Post, Body, HttpException, HttpStatus } from '@nestjs/common';
import { AppService } from './app.service';

@Controller()
export class AppController {
  constructor(private readonly appService: AppService) {}

  @Post('heartbeat')
  async registerHeartbeat(@Body() body: { serviceId: string; token: string }) {
    const { serviceId, token } = body;

    // Validate input
    if (!serviceId || !token) {
      throw new HttpException('Invalid request payload.', HttpStatus.BAD_REQUEST);
    }

    // Sanitize inputs
    const sanitizedServiceId = this.appService.sanitizeInput(serviceId);
    const sanitizedToken = this.appService.sanitizeInput(token);

    // Register heartbeat
    await this.appService.registerHeartbeat(sanitizedServiceId, sanitizedToken);
    return { message: 'Heartbeat registered successfully.' };
  }

  @Post('services')
  async getServices(@Body() body: { token: string }) {
    const { token } = body;

    // Validate input
    if (!token) {
      throw new HttpException('Invalid request payload.', HttpStatus.BAD_REQUEST);
    }

    // Sanitize input
    const sanitizedToken = this.appService.sanitizeInput(token);

    // Get services
    const services = await this.appService.getServices(sanitizedToken);
    return services;
  }
}