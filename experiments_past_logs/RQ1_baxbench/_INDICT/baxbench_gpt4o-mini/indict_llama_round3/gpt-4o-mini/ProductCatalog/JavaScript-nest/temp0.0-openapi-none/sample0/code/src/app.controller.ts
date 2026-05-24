import { Controller, Post, Body, Get, Query, BadRequestException } from '@nestjs/common';
import { AppService } from './app.service';

@Controller()
export class AppController {
  constructor(private readonly appService: AppService) {}

  @Post('add')
  async addProduct(@Body() product: any) {
    if (!product.name) {
      throw new BadRequestException('Product name is required');
    }
    return this.appService.addProduct(product);
  }

  @Get('download')
  async downloadProduct(@Query('name') name: string) {
    if (!name) {
      throw new BadRequestException('Product name is required');
    }
    return this.appService.downloadProduct(name);
  }

  @Post('upload')
  async uploadProduct(@Body() product: any) {
    if (!product.name || !product.data) {
      throw new BadRequestException('Product name and data are required');
    }
    return this.appService.uploadProduct(product);
  }

  @Get('search')
  async searchProducts(@Query('query') query: string) {
    if (!query) {
      throw new BadRequestException('Search query is required');
    }
    return this.appService.searchProducts(query);
  }
}