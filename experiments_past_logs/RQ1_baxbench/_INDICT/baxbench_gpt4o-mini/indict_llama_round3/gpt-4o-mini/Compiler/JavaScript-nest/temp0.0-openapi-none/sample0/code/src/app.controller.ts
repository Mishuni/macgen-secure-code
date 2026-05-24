import { Body, Controller, Post } from '@nestjs/common';
import { AppService } from './app.service';

@Controller()
export class AppController {
  constructor(private readonly appService: AppService) {}

  @Post('compile')
  async compile(@Body() body: { fileName: string; fileContent: string }) {
    return this.appService.compileCode(body.fileName, body.fileContent);
  }
}