import { Controller, Post, Body } from '@nestjs/common';
import { AppService } from './app.service';
import { CompileDto } from './compile.dto';

@Controller()
export class AppController {
  constructor(private readonly appService: AppService) {}

  @Post('compile')
  async compile(@Body() compileDto: CompileDto) {
    return this.appService.compile(compileDto);
  }
}