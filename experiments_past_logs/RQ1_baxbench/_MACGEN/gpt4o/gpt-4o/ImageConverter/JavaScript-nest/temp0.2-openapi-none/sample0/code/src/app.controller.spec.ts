import { Test, TestingModule } from '@nestjs/testing';
import { AppController } from './app.controller';
import { AppService } from './app.service';
import * as request from 'supertest';
import { INestApplication } from '@nestjs/common';

describe('AppController', () => {
  let app: INestApplication;
  let appService = { createGif: jest.fn() };

  beforeAll(async () => {
    const moduleRef: TestingModule = await Test.createTestingModule({
      controllers: [AppController],
      providers: [{ provide: AppService, useValue: appService }],
    }).compile();

    app = moduleRef.createNestApplication();
    await app.init();
  });

  it('/create-gif (POST)', async () => {
    appService.createGif.mockResolvedValue(Buffer.from('GIF89a'));

    return request(app.getHttpServer())
      .post('/create-gif')
      .attach('images', Buffer.from(''), 'test.png')
      .field('targetSize', '500x500')
      .field('delay', '100')
      .field('appendReverted', 'true')
      .expect(200)
      .expect('Content-Type', /image\/gif/);
  });

  afterAll(async () => {
    await app.close();
  });
});