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

  it('should return unsubscribe decision', () => {
    const result = appController.decideUnsubscribe(`From: test@example.com
    Please unsubscribe me from this mailing list.`);
    expect(result).toEqual({ email: 'test@example.com', unsubscribe: true });
  });
});