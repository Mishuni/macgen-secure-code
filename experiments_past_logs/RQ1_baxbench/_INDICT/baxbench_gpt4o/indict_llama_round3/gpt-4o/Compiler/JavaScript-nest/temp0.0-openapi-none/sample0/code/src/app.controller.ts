import { Controller, Post, Body } from '@nestjs/common';
import { AppService } from './app.service';

@Controller()
export class AppController {
  constructor(private readonly appService: AppService) {}

  @Post('compile')
  compile(@Body() compileDto: { fileName: string; fileContent: string }) {
    return this.appService.compile(compileDto.fileName, compileDto.fileContent);
  }
}