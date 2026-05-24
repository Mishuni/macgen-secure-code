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
      const result = [{ content: 'hello world!', username: 'alice' }];
      jest.spyOn(appController, 'getMessages').mockImplementation(async () => result);

      expect(await appController.getMessages()).toBe(result);
    });
  });

  describe('postMessage', () => {
    it('should return "Successful operation" on valid input', async () => {
      const message = { content: 'hello world!', username: 'alice' };
      jest.spyOn(appController, 'postMessage').mockImplementation(async () => 'Successful operation');

      expect(await appController.postMessage(message)).toBe('Successful operation');
    });
  });
});