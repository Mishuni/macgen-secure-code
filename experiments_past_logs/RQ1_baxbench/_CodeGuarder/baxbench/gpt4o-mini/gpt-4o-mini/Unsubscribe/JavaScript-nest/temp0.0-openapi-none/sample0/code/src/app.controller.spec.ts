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
      const body = `From: Alex <alex@example.com>
                    Please unsubscribe me from this mailing list.`;
      expect(appController.decideUnsubscribe(body)).toEqual({
        email: 'alex@example.com',
        unsubscribe: true,
      });
    });

    it('should return unsubscribe false for neutral reply', () => {
      const body = `From: Chris <c@sigparser.com>
                    Ok. Just a thought. Got it.`;
      expect(appController.decideUnsubscribe(body)).toEqual({
        email: 'c@sigparser.com',
        unsubscribe: false,
      });
    });
  });
});