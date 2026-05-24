import { Controller, Get, Post, Query, HttpException, HttpStatus } from '@nestjs/common';
import { AppService } from './app.service';

@Controller()
export class AppController {
  constructor(private readonly appService: AppService) {}

  @Post('click')
  async registerClick(): Promise<string> {
    try {
      await this.appService.registerClick();
      return 'Click registered successfully';
    } catch (error) {
      throw new HttpException('Invalid request', HttpStatus.BAD_REQUEST);
    }
  }

  @Get('clicks')
  async getClicks(@Query('date') date: string, @Query('direction') direction: string) {
    if (!date || !direction) {
      throw new HttpException('Invalid request', HttpStatus.BAD_REQUEST);
    }
    const validDirections = ['<', '>', '<=', '>='];
    if (!validDirections.includes(direction)) {
      throw new HttpException('Invalid request', HttpStatus.BAD_REQUEST);
    }
    const clicks = await this.appService.getClicks(date, direction);
    if (clicks.length === 0) {
      throw new HttpException('No clicks found', HttpStatus.NOT_FOUND);
    }
    return clicks;
  }
}