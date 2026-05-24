import { Controller, Post, Body, BadRequestException } from '@nestjs/common';
import { AppService } from './app.service';

@Controller()
export class AppController {
  constructor(private readonly appService: AppService) {}

  @Post('compile')
  async compile(@Body() body: { fileName: string; fileContent: string }) {
    const { fileName, fileContent } = body;
    if (!fileName || !fileContent) {
      throw new BadRequestException('Invalid input');
    }
    return this.appService.compile(fileName, fileContent);
  }
}