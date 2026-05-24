import { Test, TestingModule } from '@nestjs/testing';
import { AppController } from './app.controller';

describe('AppController', () => {
  let appController: AppController;

  beforeEach(async () => {
    const module: TestingModule = await Test.createTestingModule({
      controllers: [AppController],
    }).compile();

    appController = module.get<AppController>(AppController);
  });

  describe('decideUnsubscribe', () => {
    it('should return unsubscribe true for unsubscribe request', () => {
      const result = appController.decideUnsubscribe({ email: 'test@example.com', message: 'Please unsubscribe me from this mailing list.' });
      expect(result).toEqual({ email: 'test@example.com', unsubscribe: true });
    });

    it('should return unsubscribe false for neutral message', () => {
      const result = appController.decideUnsubscribe({ email: 'test@example.com', message: 'Just a thought.' });
      expect(result).toEqual({ email: 'test@example.com', unsubscribe: false });
    });
  });
});