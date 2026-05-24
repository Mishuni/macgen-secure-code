import { Test, TestingModule } from '@nestjs/testing';
import { AppController } from './app.controller';
import { AppService } from './app.service';

describe('AppController', () => {
  let appController: AppController;

  beforeEach(async () => {
    const module: TestingModule = await Test.createTestingModule({
      controllers: [AppController],
      providers: [AppService],
    }).compile();

    appController = module.get<AppController>(AppController);
  });

  describe('decideUnsubscribe', () => {
    it('should return unsubscribe true for unsubscribe request', () => {
      const body = 'Please unsubscribe me from this mailing list.';
      const email = 'alex@example.com';
      expect(appController.decideUnsubscribe(body)).toEqual({
        email,
        unsubscribe: true,
      });
    });

    it('should return unsubscribe false for neutral reply', () => {
      const body = 'Ok. Just a thought. Got it.';
      const email = 'unknown@example.com';
      expect(appController.decideUnsubscribe(body)).toEqual({
        email,
        unsubscribe: false,
      });
    });

    it('should handle invalid email format gracefully', () => {
      const body = 'From: invalid-email-format';
      const result = appController.decideUnsubscribe(body);
      expect(result.email).toBe('unknown@example.com');
      expect(result.unsubscribe).toBe(false);
    });
  });
});