import { Test, TestingModule } from '@nestjs/testing';
import { AppController } from './app.controller';
import { AppService } from './app.service';

describe('AppController', () => {
  let appController: AppController;
  let appService: AppService;

  beforeEach(async () => {
    const module: TestingModule = await Test.createTestingModule({
      controllers: [AppController],
      providers: [AppService],
    }).compile();

    appController = module.get<AppController>(AppController);
    appService = module.get<AppService>(AppService);
  });

  it('should be defined', () => {
    expect(appController).toBeDefined();
  });

  describe('inviteUser', () => {
    it('should return an invite id and message', async () => {
      const result = { id: 'invite123' };
      jest.spyOn(appService, 'createInvite').mockResolvedValue(result);

      expect(await appController.inviteUser({ email: 'user@example.com' })).toEqual({
        invite_id: 'invite123',
        message: 'Invitation email sent',
      });
    });
  });

  describe('createUser', () => {
    it('should return a success message', async () => {
      const message = 'User created successfully';
      jest.spyOn(appService, 'createUser').mockResolvedValue(message);

      expect(await appController.createUser({ invite_id: 'invite123', user_name: 'newuser', password: 'password' })).toEqual({
        message: 'User created successfully',
      });
    });
  });
});