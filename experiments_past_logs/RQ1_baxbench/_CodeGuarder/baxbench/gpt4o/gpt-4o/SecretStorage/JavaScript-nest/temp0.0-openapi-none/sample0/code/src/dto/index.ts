export class RegisterDto {
  email: string;
  username: string;
  password: string;
}

export class LoginDto {
  email: string;
  password: string;
}

export class SetSecretDto {
  username: string;
  secret: string;
}