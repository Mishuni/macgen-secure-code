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

  describe('getRecommendations', () => {
    it('should return an array of products', async () => {
      const result = await appController.getRecommendations('tag1,tag2');
      expect(result).toBeInstanceOf(Array);
    });
  });

  describe('postProduct', () => {
    it('should return success message', async () => {
      const result = await appController.postProduct({
        product_name: 'Test Product',
        tags: ['tag1', 'tag2'],
      });
      expect(result).toEqual({ message: 'Product added successfully' });
    });
  });
});