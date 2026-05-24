import { Body, Controller, Post } from '@nestjs/common';
import { AppService } from './app.service';

@Controller()
export class AppController {
  constructor(private readonly appService: AppService) {}

  @Post('compile')
  async compile(
    @Body() body: { fileName: string; fileContent: string },
  ): Promise<{ hasError: boolean; compilerError: string | null }> {
    return this.appService.compile(body.fileName, body.fileContent);
  }
}