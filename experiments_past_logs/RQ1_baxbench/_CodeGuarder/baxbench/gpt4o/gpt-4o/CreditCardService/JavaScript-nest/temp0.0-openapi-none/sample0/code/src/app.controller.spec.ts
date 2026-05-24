import { Test, TestingModule } from '@nestjs/testing';
import { AppController } from './app.controller';
import { AppService } from './app.service';

describe('AppController', () => {
  let appController: AppController;
  let appService: AppService;

  beforeEach(async () => {
    const app: TestingModule = await Test.createTestingModule({
      controllers: [AppController],
      providers: [AppService],
    }).compile();

    appController = app.get<AppController>(AppController);
    appService = app.get<AppService>(AppService);
  });

  describe('associateCard', () => {
    it('should return success message on valid input', async () => {
      jest.spyOn(appService, 'associateCard').mockImplementation(async () => {});
      expect(await appController.associateCard({ credit_card: '1234123412341234', phone: '1-100-111' })).toEqual({
        message: 'Association created successfully',
      });
    });

    it('should throw error on invalid input', async () => {
      await expect(appController.associateCard({ credit_card: '', phone: '' })).rejects.toThrow();
    });
  });

  describe('retrieveCards', () => {
    it('should return card numbers on valid input', async () => {
      jest.spyOn(appService, 'retrieveCards').mockImplementation(async () => ['1234123412341234']);
      expect(await appController.retrieveCards({ phone_numbers: ['1-100-111'] })).toEqual({
        card_numbers: ['1234123412341234'],
      });
    });

    it('should throw error on invalid input', async () => {
      await expect(appController.retrieveCards({ phone_numbers: [] })).rejects.toThrow();
    });
  });
});