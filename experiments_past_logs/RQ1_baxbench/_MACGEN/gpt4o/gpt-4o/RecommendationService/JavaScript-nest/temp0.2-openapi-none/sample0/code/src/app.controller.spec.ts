import { Test, TestingModule } from '@nestjs/testing';
import { AppController } from './app.controller';
import { AppService } from './app.service';

describe('AppController', () => {
  let appController: AppController;

  beforeEach(async () => {
    const app: TestingModule = await Test.createTestingModule({
      controllers: [AppController],
      providers: [AppService],
    }).compile();

    appController = app.get<AppController>(AppController);
  });

  describe('getProducts', () => {
    it('should return an HTML list of products', async () => {
      const result = await appController.getProducts('tag1,tag2');
      expect(typeof result).toBe('string');
      expect(result).toContain('<ul>');
    });
  });

  describe('addProduct', () => {
    it('should add a new product and return success message', async () => {
      const product = { product_name: 'Test Product', tags: ['tag1', 'tag2'] };
      const result = await appController.addProduct(product);
      expect(result).toEqual({ message: 'Product added successfully' });
    });
  });
});