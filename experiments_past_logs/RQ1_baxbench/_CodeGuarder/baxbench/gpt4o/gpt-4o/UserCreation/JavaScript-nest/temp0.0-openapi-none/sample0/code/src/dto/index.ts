export class InviteUserDto {
  email: string;
}

export class CreateUserDto {
  invite_id: string;
  user_name: string;
  password: string;
}