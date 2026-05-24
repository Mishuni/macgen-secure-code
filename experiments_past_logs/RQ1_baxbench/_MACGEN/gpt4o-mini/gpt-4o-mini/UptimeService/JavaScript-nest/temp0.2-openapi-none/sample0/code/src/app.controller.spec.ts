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

  it('should register heartbeat', async () => {
    const response = await appController.registerHeartbeat({ serviceId: 'my-service', token: 'pass1' });
    expect(response).toEqual({ message: 'Heartbeat registered successfully.' });
  });

  it('should get services', async () => {
    const services = await appController.getServices({ token: 'pass1' });
    expect(Array.isArray(services)).toBe(true);
  });
});