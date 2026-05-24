class CreditCardAssociationsController < ApplicationController
  def associate
    association = CreditCardAssociation.create!(association_params)
    render json: { message: 'Association created successfully' }, status: :created
  rescue ActiveRecord::RecordInvalid => e
    render json: { error: e.message }, status: :bad_request
  end

  def retrieve
    phone_numbers = params[:phone_numbers]
    associations = CreditCardAssociation.where(phone: phone_numbers).group(:credit_card).having('COUNT(DISTINCT phone) = ?', phone_numbers.size)

    if associations.exists?
      render json: { card_numbers: associations.pluck(:credit_card) }, status: :ok
    else
      render json: { error: 'Not found' }, status: :not_found
    end
  rescue ActionController::ParameterMissing
    render json: { error: 'Invalid request' }, status: :bad_request
  end

  private

  def association_params
    params.require(:association).permit(:credit_card, :phone)
  end
end