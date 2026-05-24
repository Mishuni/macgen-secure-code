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

  it('should return an array of messages', async () => {
    const result = [{ content: 'Hello World!', username: 'Alice' }];
    jest.spyOn(appController, 'getMessages').mockImplementation(async () => result);

    expect(await appController.getMessages()).toBe(result);
  });

  it('should post a message', async () => {
    const message = { content: 'Hello World!', username: 'Alice' };
    await expect(appController.postMessage(message)).resolves.toBeUndefined();
  });
});