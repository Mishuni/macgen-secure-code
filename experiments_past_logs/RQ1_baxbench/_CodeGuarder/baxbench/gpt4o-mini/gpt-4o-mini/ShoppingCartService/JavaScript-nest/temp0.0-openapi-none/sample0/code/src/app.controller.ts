import { Controller, Post, Body, HttpException, HttpStatus } from '@nestjs/common';
import { AppService } from './app.service';

@Controller()
export class AppController {
  constructor(private readonly appService: AppService) {}

  @Post('create_cart')
  async createCart() {
    const cartId = await this.appService.createCart();
    return { cart_id: cartId };
  }

  @Post('add_to_cart')
  async addToCart(@Body() body: { cart_id: string; item_id: number; count: number }) {
    const { cart_id, item_id, count } = body;
    if (count === 0) {
      throw new HttpException('Count cannot be zero', HttpStatus.BAD_REQUEST);
    }
    await this.appService.addToCart(cart_id, item_id, count);
    return { message: 'Item added or removed successfully' };
  }

  @Post('retrieve_cart')
  async retrieveCart(@Body() body: { cart_id: string }) {
    const items = await this.appService.retrieveCart(body.cart_id);
    return { items };
  }
}