import { Controller, Get, Post, Body, Query, HttpException, HttpStatus } from '@nestjs/common';
import { AppService } from './app.service';

@Controller()
export class AppController {
  constructor(private readonly appService: AppService) {}

  @Post('/add')
  async addProduct(@Body() productData: Record<string, string>) {
    if (!productData.name) {
      throw new HttpException('Invalid input', HttpStatus.BAD_REQUEST);
    }
    await this.appService.addProduct(productData);
    return { message: 'Product successfully added' };
  }

  @Get('/download')
  async downloadProduct(@Query('name') name: string) {
    if (!name) {
      throw new HttpException('Invalid input', HttpStatus.BAD_REQUEST);
    }
    const product = await this.appService.getProduct(name);
    if (!product) {
      throw new HttpException('Product not found', HttpStatus.NOT_FOUND);
    }
    return { data: product };
  }

  @Post('/upload')
  async uploadProduct(@Body() productData: { name: string; data: string }) {
    if (!productData.name || !productData.data) {
      throw new HttpException('Invalid upload query', HttpStatus.BAD_REQUEST);
    }
    await this.appService.updateProduct(productData.name, productData.data);
    return { message: 'The product with the given name was updated.' };
  }

  @Get('/search')
  async searchProducts(@Query('query') query: string) {
    if (!query) {
      throw new HttpException('Invalid search query', HttpStatus.BAD_REQUEST);
    }
    const results = await this.appService.searchProducts(query);
    return { results };
  }
}