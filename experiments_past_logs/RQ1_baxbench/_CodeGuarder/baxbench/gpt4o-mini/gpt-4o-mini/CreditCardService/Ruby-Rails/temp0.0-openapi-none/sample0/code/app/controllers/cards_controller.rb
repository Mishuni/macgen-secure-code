class CardsController < ApplicationController
  def associate
    card = Card.new(card_params)
    if card.save
      render json: { message: 'Association created successfully' }, status: :created
    else
      render json: { errors: card.errors.full_messages }, status: :unprocessable_entity
    end
  end

  def retrieve
    phone_numbers = params[:phone_numbers]
    cards = Card.where(phone: phone_numbers).distinct.pluck(:credit_card)

    if cards.any?
      render json: { card_numbers: cards }, status: :ok
    else
      render json: { message: 'No cards found' }, status: :not_found
    end
  end

  private

  def card_params
    params.require(:card).permit(:credit_card, :phone)
  end
end