import { Test, TestingModule } from '@nestjs/testing';
import { AppController } from './app.controller';
import { AppService } from './app.service';
import * as request from 'supertest';
import { INestApplication } from '@nestjs/common';

describe('AppController', () => {
  let app: INestApplication;
  let appService = { createGif: jest.fn() };

  beforeAll(async () => {
    const moduleFixture: TestingModule = await Test.createTestingModule({
      controllers: [AppController],
      providers: [{ provide: AppService, useValue: appService }],
    }).compile();

    app = moduleFixture.createNestApplication();
    await app.init();
  });

  it('/create-gif (POST) should return 400 if no images are uploaded', () => {
    return request(app.getHttpServer())
      .post('/create-gif')
      .expect(400)
      .expect({ error: 'No images uploaded' });
  });

  afterAll(async () => {
    await app.close();
  });
});