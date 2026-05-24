import { Test, TestingModule } from '@nestjs/testing';
import { AppController } from './app.controller';
import { AppService } from './app.service';
import * as request from 'supertest';
import { INestApplication } from '@nestjs/common';

describe('AppController', () => {
  let app: INestApplication;

  beforeAll(async () => {
    const moduleFixture: TestingModule = await Test.createTestingModule({
      controllers: [AppController],
      providers: [AppService],
    }).compile();

    app = moduleFixture.createNestApplication();
    await app.init();
  });

  it('should return 400 if no files are provided', async () => {
    return request(app.getHttpServer())
      .post('/concatenate')
      .expect(400)
      .expect({
        error: 'Invalid input or missing files.',
      });
  });

  afterAll(async () => {
    await app.close();
  });
});