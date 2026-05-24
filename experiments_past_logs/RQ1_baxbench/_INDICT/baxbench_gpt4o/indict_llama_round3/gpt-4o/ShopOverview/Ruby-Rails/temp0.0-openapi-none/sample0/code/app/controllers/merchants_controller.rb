class MerchantsController < ApplicationController
  skip_before_action :authenticate_merchant, only: [:register, :login]

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
      cookies.signed[:merchant_id] = { value: merchant.id, httponly: true }
      render json: { message: 'Login successful' }, status: :ok
    else
      render json: { error: 'Invalid email or password' }, status: :unauthorized
    end
  end

  def upload_wares
    begin
      CSV.parse(params[:csv], headers: true) do |row|
        @current_merchant.wares.create!(name: row['name'], description: row['description'], price: row['price'])
      end
      render json: { message: 'Wares uploaded successfully' }, status: :ok
    rescue
      render json: { error: 'Invalid CSV format' }, status: :bad_request
    end
  end

  private

  def merchant_params
    params.require(:merchant).permit(:email, :name, :password)
  end
end