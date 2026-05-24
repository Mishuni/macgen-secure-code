import { Controller, Post, Body, BadRequestException } from '@nestjs/common';
import { AppService } from './app.service';

@Controller()
export class AppController {
  constructor(private readonly appService: AppService) {}

  @Post('/search')
  async searchFiles(
    @Body('search_content') searchContent: string | null,
    @Body('search_filename') searchFilename: string | null,
    @Body('search_dir') searchDir: string | null,
  ): Promise<{ files: string[] }> {
    // Validate inputs
    if (!searchContent && !searchFilename) {
      throw new BadRequestException(
        'At least one of search_content or search_filename must be provided.',
      );
    }

    // Sanitize and validate the search directory
    const sanitizedDir = this.appService.sanitizePath(searchDir || '/data');
    if (!sanitizedDir.startsWith('/data')) {
      throw new BadRequestException('Invalid search directory.');
    }

    // Perform the search
    const files = await this.appService.searchFiles(
      searchContent,
      searchFilename,
      sanitizedDir,
    );

    return { files };
  }
}