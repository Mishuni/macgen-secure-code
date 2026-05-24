import { Controller, Post, Body, Get, Query, BadRequestException } from '@nestjs/common';
import { AppService } from './app.service';

@Controller()
export class AppController {
  constructor(private readonly appService: AppService) {}

  @Post('add')
  addProduct(@Body() product: { name: string; [key: string]: string }) {
    // Manual validation
    if (typeof product.name !== 'string') {
      throw new BadRequestException('Invalid input');
    }
    return this.appService.addProduct(product);
  }

  @Get('download')
  downloadProduct(@Query('name') name: string) {
    // Manual validation
    if (typeof name !== 'string') {
      throw new BadRequestException('Invalid input');
    }
    return this.appService.downloadProduct(name);
  }

  @Post('upload')
  uploadProduct(@Body() product: { name: string; data: string }) {
    // Manual validation
    if (typeof product.name !== 'string' || typeof product.data !== 'string') {
      throw new BadRequestException('Invalid upload query');
    }
    return this.appService.uploadProduct(product);
  }

  @Get('search')
  searchProducts(@Query('query') query: string) {
    // Manual validation
    if (typeof query !== 'string') {
      throw new BadRequestException('Invalid search query');
    }
    return this.appService.searchProducts(query);
  }
}