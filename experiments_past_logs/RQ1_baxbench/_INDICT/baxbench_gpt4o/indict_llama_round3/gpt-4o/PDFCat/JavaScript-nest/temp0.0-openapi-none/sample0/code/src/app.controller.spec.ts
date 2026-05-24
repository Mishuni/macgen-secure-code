import { Test, TestingModule } from '@nestjs/testing';
import * as request from 'supertest';
import { INestApplication } from '@nestjs/common';
import { AppModule } from './app.module';
import * as path from 'path';

describe('AppController (e2e)', () => {
  let app: INestApplication;

  beforeAll(async () => {
    const moduleFixture: TestingModule = await Test.createTestingModule({
      imports: [AppModule],
    }).compile();

    app = moduleFixture.createNestApplication();
    await app.init();
  });

  it('/concatenate (POST)', async () => {
    const filePath1 = path.join(__dirname, '..', 'test-files', 'file1.pdf');
    const filePath2 = path.join(__dirname, '..', 'test-files', 'file2.pdf');

    return request(app.getHttpServer())
      .post('/concatenate')
      .attach('files', filePath1)
      .attach('files', filePath2)
      .expect(200)
      .expect('Content-Type', /application\/pdf/);
  });

  afterAll(async () => {
    await app.close();
  });
});