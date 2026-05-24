import { Controller, Post, Body, Get, Query } from '@nestjs/common';
import { AppService } from './app.service';

@Controller()
export class AppController {
  constructor(private readonly appService: AppService) {}

  @Post('add')
  async addProduct(@Body() product: { name: string; [key: string]: any }) {
    return this.appService.addProduct(product);
  }

  @Get('download')
  async downloadProduct(@Query('name') name: string) {
    return this.appService.downloadProduct(name);
  }

  @Post('upload')
  async uploadProduct(@Body() product: { name: string; data: string }) {
    return this.appService.uploadProduct(product);
  }

  @Get('search')
  async searchProducts(@Query('query') query: string) {
    return this.appService.searchProducts(query);
  }
}