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
    it('should return unsubscribe true for valid unsubscribe request', async () => {
      const emailContent = `
        MIME-Version:1.0
        From:Alex <alex@example.com>
        Subject:Re:Newsletter Subscription
        Content-Type:text/plain; charset="UTF-8"

        Please unsubscribe me from this mailing list.
      `;
      const result = await appController.decideUnsubscribe({ email: emailContent });
      expect(result).toEqual({ email: 'alex@example.com', unsubscribe: true });
    });

    it('should return unsubscribe false for neutral email', async () => {
      const emailContent = `
        MIME-Version:1.0
        From:Chris <c@sigparser.com>
        Subject:Re:food for thought
        Content-Type:text/plain; charset="UTF-8"

        Ok. Just a thought. Got it.
      `;
      const result = await appController.decideUnsubscribe({ email: emailContent });
      expect(result).toEqual({ email: 'c@sigparser.com', unsubscribe: false });
    });
  });
});