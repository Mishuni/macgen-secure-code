import { Controller, Post, Body, HttpCode, HttpStatus } from '@nestjs/common';

@Controller('compile')
export class AppController {
  constructor(private readonly appService: AppService) {}

  @Post()
  @HttpCode(HttpStatus.OK)
  async compile(@Body() body: { fileName: string; fileContent: string }) {
    const { fileName, fileContent } = body;

    // Validate input
    if (!fileName || !fileContent) {
      throw new BadRequestException('fileName and fileContent are required');
    }

    // Call the service to compile the code
    return this.appService.compileCode(fileName, fileContent);
  }
}