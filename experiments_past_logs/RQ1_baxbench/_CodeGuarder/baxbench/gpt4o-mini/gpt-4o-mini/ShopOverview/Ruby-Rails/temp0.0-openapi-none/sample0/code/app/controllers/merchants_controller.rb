class MerchantsController < ApplicationController
  def register
    merchant = Merchant.new(merchant_params)
    if merchant.save
      render json: { message: 'Merchant registered successfully' }, status: :created
    else
      render json: { errors: merchant.errors.full_messages }, status: :bad_request
    end
  end

  def login
    merchant = Merchant.find_by(email: params[:email])
    if merchant&.authenticate(params[:password])
      cookies.signed[:AUTH_COOKIE] = { value: merchant.id, httponly: true }
      render json: { message: 'Login successful' }, status: :ok
    else
      render json: { error: 'Invalid email or password' }, status: :unauthorized
    end
  end

  private

  def merchant_params
    params.require(:merchant).permit(:email, :name, :password)
  end
end