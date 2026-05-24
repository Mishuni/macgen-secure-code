import { Test, TestingModule } from '@nestjs/testing';
import { INestApplication } from '@nestjs/common';
import * as request from 'supertest';
import { AppModule } from './app.module';
import * as fs from 'fs';
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

  it('/concatenate (POST) should concatenate PDF files', async () => {
    const file1 = path.join(__dirname, '../test-files/file1.pdf');
    const file2 = path.join(__dirname, '../test-files/file2.pdf');

    const response = await request(app.getHttpServer())
      .post('/concatenate')
      .attach('files', file1)
      .attach('files', file2)
      .expect(200);

    expect(response.headers['content-type']).toBe('application/pdf');
    expect(response.body).toBeDefined();
  });

  afterAll(async () => {
    await app.close();
  });
});