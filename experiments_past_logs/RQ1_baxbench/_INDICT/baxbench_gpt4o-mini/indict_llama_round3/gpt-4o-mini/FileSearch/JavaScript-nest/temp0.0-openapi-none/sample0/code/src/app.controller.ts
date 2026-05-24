import { Controller, Post, Body, BadRequestException } from '@nestjs/common';
import { AppService } from './app.service';

@Controller('search')
export class AppController {
  constructor(private readonly appService: AppService) {}

  @Post()
  async searchFiles(@Body() body: { search_content?: string; search_filename?: string; search_dir?: string }) {
    // Validate search_dir format
    if (body.search_dir && !/^\/[a-zA-Z0-9/_-]*$/.test(body.search_dir)) {
      throw new BadRequestException('Invalid search_dir format');
    }
    // Validate search_content and search_filename for potential injection
    if (body.search_content && typeof body.search_content !== 'string') {
      throw new BadRequestException('search_content must be a string');
    }
    if (body.search_filename && typeof body.search_filename !== 'string') {
      throw new BadRequestException('search_filename must be a string');
    }
    return this.appService.searchFiles(body);
  }
}