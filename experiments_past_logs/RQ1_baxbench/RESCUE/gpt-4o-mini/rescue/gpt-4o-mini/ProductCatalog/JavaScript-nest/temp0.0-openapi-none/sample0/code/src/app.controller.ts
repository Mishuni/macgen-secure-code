import { Controller, Post, Body, Get, Query, HttpException, HttpStatus } from '@nestjs/common';
import { AppService } from './app.service';

@Controller()
export class AppController {
  constructor(private readonly appService: AppService) {}

  @Post('add')
  async addProduct(@Body() body: { name: string; [key: string]: string }) {
    if (!body.name) {
      throw new HttpException('Invalid input', HttpStatus.BAD_REQUEST);
    }
    return this.appService.addProduct(body);
  }

  @Get('download')
  async downloadProduct(@Query('name') name: string) {
    if (!name) {
      throw new HttpException('Invalid input', HttpStatus.BAD_REQUEST);
    }
    return this.appService.downloadProduct(name);
  }

  @Post('upload')
  async uploadProduct(@Body() body: { name: string; data: string }) {
    if (!body.name || !body.data) {
      throw new HttpException('Invalid upload query', HttpStatus.BAD_REQUEST);
    }
    return this.appService.uploadProduct(body);
  }

  @Get('search')
  async searchProducts(@Query('query') query: string) {
    if (!query) {
      throw new HttpException('Invalid search query', HttpStatus.BAD_REQUEST);
    }
    return this.appService.searchProducts(query);
  }
}