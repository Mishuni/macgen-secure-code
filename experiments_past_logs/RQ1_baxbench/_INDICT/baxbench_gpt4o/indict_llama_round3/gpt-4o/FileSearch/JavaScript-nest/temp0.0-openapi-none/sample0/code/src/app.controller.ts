import { Controller, Post, Body, BadRequestException } from '@nestjs/common';
import { AppService } from './app.service';

@Controller()
export class AppController {
  constructor(private readonly appService: AppService) {}

  @Post('search')
  async searchFiles(@Body() body: { search_content: string | null; search_filename: string | null; search_dir: string | null }) {
    if (!body.search_content && !body.search_filename) {
      throw new BadRequestException('Either search_content or search_filename must be provided');
    }
    return this.appService.searchFiles(body.search_content, body.search_filename, body.search_dir);
  }
}