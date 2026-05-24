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
        Date:Thu, 10 Jan 2019 14:21:11 -0800
        Subject:Re:Newsletter Subscription
        To:Paul <p@sigparser.com>
        Content-Type:text/plain; charset="UTF-8"
        
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
        Date:Wed, 9 Jan 2019 08:36:15 -0800
        Subject:Re:food for thought
        To:Paul <p@sigparser.com>
        Content-Type:text/plain; charset="UTF-8"
        
        Ok. Just a thought. Got it.
      `;
      expect(appController.decideUnsubscribe(emailContent)).toEqual({
        email: 'c@sigparser.com',
        unsubscribe: false,
      });
    });
  });
});