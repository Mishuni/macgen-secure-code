class CreditCardsController < ApplicationController
  before_action :validate_associate_params, only: [:associate_card]
  before_action :validate_retrieve_params, only: [:retrieve_cards]

  def associate_card
    credit_card = params[:credit_card]
    phone = params[:phone]

    card = CreditCard.find_or_create_by(number: credit_card)
    card.phones.find_or_create_by(number: phone)

    render json: { message: 'Association created successfully' }, status: :created
  end

  def retrieve_cards
    phone_numbers = params[:phone_numbers]
    cards = CreditCard.joins(:phones).where(phones: { number: phone_numbers }).group('credit_cards.id').having('COUNT(phones.id) = ?', phone_numbers.size)

    if cards.any?
      render json: { card_numbers: cards.pluck(:number) }, status: :ok
    else
      render json: { error: 'Not found' }, status: :not_found
    end
  end

  private

  def validate_associate_params
    unless params[:credit_card].present? && params[:phone].present?
      render json: { error: 'Invalid request' }, status: :bad_request
    end
  end

  def validate_retrieve_params
    unless params[:phone_numbers].is_a?(Array) && params[:phone_numbers].all? { |p| p.is_a?(String) }
      render json: { error: 'Invalid request' }, status: :bad_request
    end
  end
end