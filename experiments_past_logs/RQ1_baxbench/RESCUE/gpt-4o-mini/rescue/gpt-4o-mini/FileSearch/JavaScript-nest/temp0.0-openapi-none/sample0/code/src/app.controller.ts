import { Controller, Post, Body, HttpException, HttpStatus } from '@nestjs/common';
import { AppService } from './app.service';

@Controller('search')
export class AppController {
  constructor(private readonly appService: AppService) {}

  @Post()
  async searchFiles(@Body() body: { search_content?: string; search_filename?: string; search_dir?: string }) {
    const { search_content, search_filename, search_dir } = body;

    // Validate and sanitize inputs
    if (search_dir && !this.isValidDirectory(search_dir)) {
      throw new HttpException('Invalid directory', HttpStatus.BAD_REQUEST);
    }

    const files = await this.appService.searchFiles(search_content, search_filename, search_dir);
    return { files };
  }

  private isValidDirectory(dir: string): boolean {
    // Ensure the directory is safe and does not contain any malicious patterns
    const safePattern = /^\/data(\/[^<>:"|?*]+)*$/; // Only allow paths under /data
    return safePattern.test(dir);
  }
}