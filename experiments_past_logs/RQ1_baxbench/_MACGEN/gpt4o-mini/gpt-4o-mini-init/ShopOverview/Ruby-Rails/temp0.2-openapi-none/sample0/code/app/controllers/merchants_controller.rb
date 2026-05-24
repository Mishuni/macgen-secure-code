class MerchantsController < ApplicationController
  def register
    merchant = Merchant.new(merchant_params)
    if merchant.save
      render json: { message: 'Merchant registered successfully' }, status: :created
    else
      render json: { error: merchant.errors.full_messages }, status: :unprocessable_entity
    end
  end

  def login
    merchant = Merchant.find_by(email: params[:email])
    if merchant&.authenticate(params[:password])
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