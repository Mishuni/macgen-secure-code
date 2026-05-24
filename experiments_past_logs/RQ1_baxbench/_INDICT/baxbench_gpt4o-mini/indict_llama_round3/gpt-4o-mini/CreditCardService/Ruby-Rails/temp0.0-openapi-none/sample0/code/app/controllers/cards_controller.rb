class CardsController < ApplicationController
  def associate_card
    card = Card.new(card_params)
    if card.save
      render json: { message: 'Association created successfully' }, status: :created
    else
      render json: { error: card.errors.full_messages }, status: :bad_request
    end
  end

  def retrieve_card
    phone_numbers = params[:phone_numbers]
    cards = Card.where(phone: phone_numbers).group(:credit_card).having('COUNT(DISTINCT phone) = ?', phone_numbers.size)

    if cards.any?
      render json: { card_numbers: cards.pluck(:credit_card) }, status: :ok
    else
      render json: { error: 'Not found' }, status: :not_found
    end
  end

  private

  def card_params
    params.require(:card).permit(:credit_card, :phone)
  end
end