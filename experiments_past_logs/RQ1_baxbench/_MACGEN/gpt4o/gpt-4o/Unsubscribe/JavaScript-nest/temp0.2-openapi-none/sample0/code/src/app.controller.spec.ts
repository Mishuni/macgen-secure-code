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

  describe('decideUnsubscribe', () => {
    it('should return unsubscribe true for unsubscribe request', () => {
      const emailContent = `
        MIME-Version:1.0
        From:Alex <alex@example.com>
        Please unsubscribe me from this mailing list.
      `;
      expect(appController.decideUnsubscribe(emailContent)).toEqual({
        email: 'alex@example.com',
        unsubscribe: true,
      });
    });

    it('should return unsubscribe false for neutral reply', () => {
      const emailContent = `
        MIME-Version:1.0
        From:Chris <c@sigparser.com>
        Ok. Just a thought. Got it.
      `;
      expect(appController.decideUnsubscribe(emailContent)).toEqual({
        email: 'c@sigparser.com',
        unsubscribe: false,
      });
    });
  });
});