import { Controller, Get, Query, BadRequestException } from '@nestjs/common';
import { AppService } from './app.service';

@Controller('search')
export class AppController {
  constructor(private readonly appService: AppService) {}

  @Get()
  async searchFiles(
    @Query('regex') regex: string,
    @Query('directory') directory?: string,
    @Query('recursive') recursive: boolean = false,
  ) {
    if (!this.isValidRegex(regex)) {
      throw new BadRequestException('Invalid regex pattern.');
    }
    return this.appService.searchFiles(regex, directory, recursive);
  }

  private isValidRegex(regex: string): boolean {
    try {
      new RegExp(regex);
      return true;
    } catch {
      return false;
    }
  }
}