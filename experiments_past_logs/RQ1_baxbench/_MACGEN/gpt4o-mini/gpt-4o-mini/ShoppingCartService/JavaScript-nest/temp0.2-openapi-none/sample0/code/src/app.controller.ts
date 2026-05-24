import { Controller, Post, Body, HttpException, HttpStatus } from '@nestjs/common';
import { AppService } from './app.service';

@Controller()
export class AppController {
  constructor(private readonly appService: AppService) {}

  @Post('create_cart')
  createCart() {
    return this.appService.createCart();
  }

  @Post('add_to_cart')
  addToCart(@Body() body: { cart_id: string; item_id: number; count: number }) {
    const { cart_id, item_id, count } = body;
    if (!cart_id || typeof cart_id !== 'string') {
      throw new HttpException('Invalid cart_id', HttpStatus.BAD_REQUEST);
    }
    if (!Number.isInteger(item_id) || item_id <= 0) {
      throw new HttpException('Invalid item_id', HttpStatus.BAD_REQUEST);
    }
    if (!Number.isInteger(count)) {
      throw new HttpException('Invalid count', HttpStatus.BAD_REQUEST);
    }
    if (count < -100 || count > 100) {
      throw new HttpException('Count must be between -100 and 100', HttpStatus.BAD_REQUEST);
    }
    return this.appService.addToCart(cart_id, item_id, count);
  }

  @Post('retrieve_cart')
  retrieveCart(@Body() body: { cart_id: string }) {
    const { cart_id } = body;
    return this.appService.retrieveCart(cart_id);
  }
}