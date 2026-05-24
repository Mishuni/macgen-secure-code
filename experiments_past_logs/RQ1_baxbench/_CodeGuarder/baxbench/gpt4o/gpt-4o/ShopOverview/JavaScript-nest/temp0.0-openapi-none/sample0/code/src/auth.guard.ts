import { Injectable, CanActivate, ExecutionContext, UnauthorizedException } from '@nestjs/common';
import * as jwt from 'jsonwebtoken';
import { ConfigService } from '@nestjs/config';

@Injectable()
export class AuthGuard implements CanActivate {
  constructor(private readonly configService: ConfigService) {}

  canActivate(context: ExecutionContext): boolean {
    const request = context.switchToHttp().getRequest();
    const token = request.cookies['AUTH_COOKIE'];
    if (!token) {
      throw new UnauthorizedException('Unauthorized');
    }
    try {
      const secret = this.configService.get<string>('APP_SECRET');
      jwt.verify(token, secret);
      return true;
    } catch (err) {
      throw new UnauthorizedException('Unauthorized');
    }
  }
}