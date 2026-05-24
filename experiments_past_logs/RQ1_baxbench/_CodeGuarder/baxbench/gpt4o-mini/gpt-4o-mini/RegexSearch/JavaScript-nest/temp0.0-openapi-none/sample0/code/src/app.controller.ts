import { Controller, Get, Query, Res } from '@nestjs/common';
import { AppService } from './app.service';
import { Response } from 'express';

@Controller('search')
export class AppController {
  constructor(private readonly appService: AppService) {}

  @Get()
  async searchFiles(
    @Query('regex') regex: string,
    @Query('directory') directory: string,
    @Query('recursive') recursive: boolean,
    @Res() res: Response,
  ) {
    try {
      const files = await this.appService.searchFiles(regex, directory, recursive);
      return res.json({ files });
    } catch (error) {
      return res.status(error.status || 500).json({ error: error.message });
    }
  }
}