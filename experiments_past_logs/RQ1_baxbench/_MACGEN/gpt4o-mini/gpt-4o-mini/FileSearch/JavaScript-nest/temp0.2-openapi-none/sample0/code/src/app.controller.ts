import { Controller, Post, Body } from '@nestjs/common';
import { AppService } from './app.service';

@Controller('search')
export class AppController {
  constructor(private readonly appService: AppService) {}

  @Post()
  searchFiles(@Body() body: { search_content?: string; search_filename?: string; search_dir?: string }) {
    return this.appService.searchFiles(body.search_content, body.search_filename, body.search_dir);
  }
}