import { Controller, Get, Query, BadRequestException } from '@nestjs/common';
import { AppService } from './app.service';

@Controller()
export class AppController {
  constructor(private readonly appService: AppService) {}

  @Get('search')
  async searchFiles(
    @Query('regex') regex: string,
    @Query('directory') directory: string = '',
    @Query('recursive') recursive: string = 'false',
  ) {
    if (!regex) {
      throw new BadRequestException('Regex query parameter is required');
    }

    const isRecursive = recursive === 'true';
    try {
      const files = await this.appService.searchFiles(regex, directory, isRecursive);
      return { files };
    } catch (error) {
      throw new BadRequestException(error.message);
    }
  }
}