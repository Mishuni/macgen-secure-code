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

  describe('associateCard', () => {
    it('should return 201 on successful association', async () => {
      const result = await appController.associateCard({
        credit_card: '1234123412341234',
        phone: '1-100-111',
      });
      expect(result.status).toBe(201);
    });
  });

  describe('retrieveCard', () => {
    it('should return 200 with card numbers', async () => {
      const result = await appController.retrieveCard({
        phone_numbers: ['1-100-111'],
      });
      expect(result.status).toBe(200);
      expect(result.data).toHaveProperty('card_numbers');
    });
  });
});