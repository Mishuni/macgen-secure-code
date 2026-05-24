class CreditCardsController < ApplicationController
  def associate_card
    credit_card = params[:credit_card]
    phone = params[:phone]

    if credit_card.blank? || phone.blank?
      render json: { error: 'Invalid request' }, status: :bad_request
      return
    end

    association = CreditCardPhoneAssociation.find_or_create_by(credit_card: credit_card, phone: phone)
    if association.persisted?
      render json: { message: 'Association created successfully' }, status: :created
    else
      render json: { error: 'Failed to create association' }, status: :unprocessable_entity
    end
  end

  def retrieve_cards
    phone_numbers = params[:phone_numbers]

    if phone_numbers.blank? || !phone_numbers.is_a?(Array)
      render json: { error: 'Invalid request' }, status: :bad_request
      return
    end

    card_numbers = CreditCardPhoneAssociation.where(phone: phone_numbers)
                                             .group(:credit_card)
                                             .having('COUNT(DISTINCT phone) = ?', phone_numbers.size)
                                             .pluck(:credit_card)

    if card_numbers.any?
      render json: { card_numbers: card_numbers }, status: :ok
    else
      render json: { error: 'Not found' }, status: :not_found
    end
  end
end