import {
  Controller,
  Post,
  Body,
  Get,
  Query,
  Res,
  HttpException,
  HttpStatus,
} from '@nestjs/common';
import { AppService } from './app.service';

@Controller()
export class AppController {
  constructor(private readonly appService: AppService) {}

  @Post('/add')
  async addProduct(@Body() body: any, @Res() res: any) {
    const { name, ...data } = body;

    if (!name || typeof name !== 'string') {
      throw new HttpException('Invalid input', HttpStatus.BAD_REQUEST);
    }

    try {
      const sanitizedData = JSON.stringify(data);
      await this.appService.addProduct(name, sanitizedData);
      res.status(HttpStatus.CREATED).send({ message: 'Product added' });
    } catch (error) {
      if (error.code === 'SQLITE_CONSTRAINT') {
        throw new HttpException('Product already exists', HttpStatus.BAD_REQUEST);
      }
      throw new HttpException('Internal Server Error', HttpStatus.INTERNAL_SERVER_ERROR);
    }
  }

  @Get('/download')
  async downloadProduct(@Query('name') name: string, @Res() res: any) {
    if (!name || typeof name !== 'string') {
      throw new HttpException('Invalid input', HttpStatus.BAD_REQUEST);
    }

    const product = await this.appService.getProductByName(name);
    if (!product) {
      throw new HttpException('Product not found', HttpStatus.NOT_FOUND);
    }

    res.status(HttpStatus.OK).send({ data: product.data });
  }

  @Post('/upload')
  async uploadProduct(@Body() body: any, @Res() res: any) {
    const { name, data } = body;

    if (!name || typeof name !== 'string' || !data || typeof data !== 'string') {
      throw new HttpException('Invalid input', HttpStatus.BAD_REQUEST);
    }

    const product = await this.appService.getProductByName(name);
    if (!product) {
      throw new HttpException('Product not found', HttpStatus.NOT_FOUND);
    }

    await this.appService.updateProduct(name, data);
    res.status(HttpStatus.OK).send({ message: 'Product updated' });
  }

  @Get('/search')
  async searchProducts(@Query('query') query: string, @Res() res: any) {
    if (!query || typeof query !== 'string') {
      throw new HttpException('Invalid input', HttpStatus.BAD_REQUEST);
    }

    const results = await this.appService.searchProducts(query);
    res.status(HttpStatus.OK).send({ results });
  }
}