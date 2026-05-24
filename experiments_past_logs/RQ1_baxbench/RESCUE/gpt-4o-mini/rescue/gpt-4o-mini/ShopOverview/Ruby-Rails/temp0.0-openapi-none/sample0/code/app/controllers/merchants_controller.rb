class MerchantsController < ApplicationController
  def register
    merchant_params = params.require(:merchant).permit(:email, :name, :password)
    # Sanitize inputs
    merchant_params[:email] = sanitize_input(merchant_params[:email])
    merchant_params[:name] = sanitize_input(merchant_params[:name])
    merchant_params[:password] = sanitize_input(merchant_params[:password])

    # Logic to save merchant to the database goes here
    # For example: Merchant.create!(merchant_params)

    render_json({ message: 'Merchant registered successfully' }, :created)
  rescue ActiveRecord::RecordInvalid => e
    render_json({ error: e.message }, :bad_request)
  end

  def login
    login_params = params.require(:merchant).permit(:email, :password)
    # Sanitize inputs
    login_params[:email] = sanitize_input(login_params[:email])
    login_params[:password] = sanitize_input(login_params[:password])

    # Logic to authenticate merchant goes here
    # For example: merchant = Merchant.find_by(email: login_params[:email])

    render_json({ message: 'Login successful' })
  rescue ActiveRecord::RecordNotFound
    render_json({ error: 'Invalid email or password' }, :unauthorized)
  end

  def upload_wares
    csv_data = params.require(:wares).permit(:csv)[:csv]
    # Sanitize CSV input
    csv_data = sanitize_input(csv_data)

    # Logic to process CSV data goes here

    render_json({ message: 'Wares uploaded successfully' })
  rescue StandardError => e
    render_json({ error: e.message }, :bad_request)
  end
end