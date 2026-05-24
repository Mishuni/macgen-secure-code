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
      throw new HttpException('Invalid request: count cannot be zero', HttpStatus.BAD_REQUEST);
    }

    if (count < 0) {
      const currentCount = await this.appService.getItemCount(cart_id, item_id);
      if (currentCount + count < 0) {
        throw new HttpException('Invalid request: cannot remove more items than present', HttpStatus.BAD_REQUEST);
      }
    }

    const result = await this.appService.addToCart(cart_id, item_id, count);
    if (result === null) {
      throw new HttpException('Cart not found', HttpStatus.NOT_FOUND);
    }
    return { message: 'Item added or removed successfully' };
  }

  @Post('retrieve_cart')
  async retrieveCart(@Body() body: { cart_id: string }) {
    const { cart_id } = body;
    const items = await this.appService.retrieveCart(cart_id);
    if (items === null) {
      throw new HttpException('Cart not found', HttpStatus.NOT_FOUND);
    }
    return { items };
  }
}