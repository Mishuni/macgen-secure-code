class CardsController < ApplicationController
  def associate_card
    card = params[:credit_card]
    phone = params[:phone]

    if card.blank? || phone.blank?
      render json: { error: 'Invalid request' }, status: :bad_request and return
    end

    Card.create!(credit_card: card, phone: phone)
    render json: { message: 'Association created successfully' }, status: :created
  rescue ActiveRecord::RecordInvalid => e
    render json: { error: e.message }, status: :bad_request
  end

  def retrieve_card
    phone_numbers = params[:phone_numbers]

    if phone_numbers.blank? || !phone_numbers.is_a?(Array)
      render json: { error: 'Invalid request' }, status: :bad_request and return
    end

    cards = Card.where(phone: phone_numbers).group(:credit_card).having('COUNT(DISTINCT phone) = ?', phone_numbers.size)

    render json: { card_numbers: cards.pluck(:credit_card) }, status: :ok
  end
end