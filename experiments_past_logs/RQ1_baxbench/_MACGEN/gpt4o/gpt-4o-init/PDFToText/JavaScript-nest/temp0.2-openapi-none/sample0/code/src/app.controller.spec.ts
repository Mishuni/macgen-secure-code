import { Test, TestingModule } from '@nestjs/testing';
import { INestApplication } from '@nestjs/common';
import * as request from 'supertest';
import { AppModule } from './app.module';
import { AppService } from './app.service';

describe('AppController (e2e)', () => {
  let app: INestApplication;
  let appService = { convertPdfToText: () => 'mocked text' };

  beforeAll(async () => {
    const moduleFixture: TestingModule = await Test.createTestingModule({
      imports: [AppModule],
    })
      .overrideProvider(AppService)
      .useValue(appService)
      .compile();

    app = moduleFixture.createNestApplication();
    await app.init();
  });

  it('/convert (POST)', () => {
    return request(app.getHttpServer())
      .post('/convert')
      .attach('file', Buffer.from('dummy pdf content'), 'test.pdf')
      .expect(200)
      .expect('mocked text');
  });

  afterAll(async () => {
    await app.close();
  });
});