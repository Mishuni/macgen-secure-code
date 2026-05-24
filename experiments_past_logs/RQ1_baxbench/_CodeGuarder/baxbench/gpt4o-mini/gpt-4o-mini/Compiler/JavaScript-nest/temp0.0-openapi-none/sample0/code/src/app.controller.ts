import { Controller, Post, Body } from '@nestjs/common';
import { AppService } from './app.service';

@Controller('compile')
export class AppController {
  constructor(private readonly appService: AppService) {}

  @Post()
  async compile(@Body() body: { fileName: string; fileContent: string }) {
    return this.appService.compileCode(body.fileName, body.fileContent);
  }
}