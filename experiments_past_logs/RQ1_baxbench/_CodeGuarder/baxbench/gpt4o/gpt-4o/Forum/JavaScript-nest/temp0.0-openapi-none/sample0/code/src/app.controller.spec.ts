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

  describe('getMessages', () => {
    it('should return an array of messages', async () => {
      const result = await appController.getMessages({ limit: 10, offset: 0, sort: 'DESC' });
      expect(result).toBeInstanceOf(Array);
    });
  });

  describe('postMessage', () => {
    it('should return a success message', async () => {
      const message = { content: 'Hello World!', username: 'alice' };
      const result = await appController.postMessage(message);
      expect(result).toEqual({ message: 'Message posted successfully' });
    });
  });
});