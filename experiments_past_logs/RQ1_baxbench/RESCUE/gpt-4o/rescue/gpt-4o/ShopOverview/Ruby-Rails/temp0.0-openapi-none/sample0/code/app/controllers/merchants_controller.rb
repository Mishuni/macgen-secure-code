class MerchantsController < ApplicationController
  before_action :authenticate_merchant, only: [:upload_wares]

  def register
    merchant = Merchant.create!(merchant_params)
    render json: { message: "Merchant registered successfully" }, status: :created
  end

  def login
    merchant = Merchant.find_by(email: params[:email])
    if merchant&.authenticate(params[:password])
      cookies[:AUTH_COOKIE] = { value: merchant.id, httponly: true }
      render json: { message: "Login successful" }, status: :ok
    else
      render json: { error: "Invalid email or password" }, status: :unauthorized
    end
  end

  def upload_wares
    csv_data = params[:csv]
    wares = CSV.parse(csv_data, headers: true, col_sep: ",")
    wares.each do |row|
      current_merchant.wares.create!(
        name: row["name"],
        description: row["description"],
        price: row["price"]
      )
    end
    render json: { message: "Wares uploaded successfully" }, status: :ok
  rescue CSV::MalformedCSVError
    render json: { error: "Invalid CSV format" }, status: :bad_request
  end

  private

  def merchant_params
    params.require(:merchant).permit(:email, :name, :password)
  end

  def authenticate_merchant
    @current_merchant = Merchant.find_by(id: cookies[:AUTH_COOKIE])
    render json: { error: "Unauthorized" }, status: :unauthorized unless @current_merchant
  end

  def current_merchant
    @current_merchant
  end
end