import { Controller, Get, Post, Query, Res, HttpStatus } from '@nestjs/common';
import { AppService } from './app.service';
import { Response } from 'express';

@Controller()
export class AppController {
  constructor(private readonly appService: AppService) {}

  @Post('click')
  async registerClick(@Res() res: Response) {
    try {
      await this.appService.registerClick();
      return res.status(HttpStatus.CREATED).send('Click registered successfully');
    } catch (error) {
      return res.status(HttpStatus.INTERNAL_SERVER_ERROR).send('Error registering click');
    }
  }

  @Get('clicks')
  async getClicks(
    @Query('date') date: string,
    @Query('direction') direction: string,
    @Res() res: Response,
  ) {
    if (!date || !direction || !['<', '>', '<=', '>='].includes(direction)) {
      return res.status(HttpStatus.BAD_REQUEST).send('Invalid request');
    }

    if (isNaN(Date.parse(date))) {
      return res.status(HttpStatus.BAD_REQUEST).send('Invalid date format');
    }

    try {
      const clicks = await this.appService.getClicks(date, direction);
      if (clicks.length === 0) {
        return res.status(HttpStatus.NOT_FOUND).send('No clicks found');
      }
      return res.status(HttpStatus.OK).json(clicks);
    } catch (error) {
      return res.status(HttpStatus.INTERNAL_SERVER_ERROR).send('Error retrieving clicks');
    }
  }
}