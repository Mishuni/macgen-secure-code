import { Test, TestingModule } from '@nestjs/testing';
import { AppController } from './app.controller';
import { AppService } from './app.service';

describe('AppController', () => {
  let appController: AppController;
  let appService: AppService;

  beforeEach(async () => {
    const app: TestingModule = await Test.createTestingModule({
      controllers: [AppController],
      providers: [
        {
          provide: AppService,
          useValue: {
            associateCard: jest.fn(),
            retrieveCards: jest.fn(),
          },
        },
      ],
    }).compile();

    appController = app.get<AppController>(AppController);
    appService = app.get<AppService>(AppService);
  });

  describe('associateCard', () => {
    it('should return success message on valid input', async () => {
      jest.spyOn(appService, 'associateCard').mockResolvedValueOnce();
      const result = await appController.associateCard('1234123412341234', '1-100-111');
      expect(result).toEqual({ message: 'Association created successfully' });
    });

    it('should throw an error on invalid input', async () => {
      await expect(appController.associateCard('', '')).rejects.toThrow();
    });
  });

  describe('retrieveCards', () => {
    it('should return card numbers on valid input', async () => {
      jest.spyOn(appService, 'retrieveCards').mockResolvedValueOnce(['1234123412341234']);
      const result = await appController.retrieveCards(['1-100-111']);
      expect(result).toEqual({ card_numbers: ['1234123412341234'] });
    });

    it('should throw an error if no phone numbers are provided', async () => {
      await expect(appController.retrieveCards([])).rejects.toThrow();
    });

    it('should throw a not found error if no cards are found', async () => {
      jest.spyOn(appService, 'retrieveCards').mockResolvedValueOnce([]);
      await expect(appController.retrieveCards(['1-100-111'])).rejects.toThrow();
    });
  });
});