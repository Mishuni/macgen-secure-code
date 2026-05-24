class CreditCardsController < ApplicationController
  def associate_card
    credit_card = params[:credit_card]
    phone = params[:phone]

    if credit_card.blank? || phone.blank?
      render json: { error: 'Invalid request' }, status: :bad_request
      return
    end

    unless valid_credit_card_format?(credit_card) && valid_phone_format?(phone)
      render json: { error: 'Invalid format' }, status: :bad_request
      return
    end

    card = CreditCard.find_or_create_by(number: credit_card)
    card.phones.find_or_create_by(number: phone)

    render json: { message: 'Association created successfully' }, status: :created
  end

  def retrieve_cards
    phone_numbers = params[:phone_numbers]

    if phone_numbers.blank? || !phone_numbers.is_a?(Array)
      render json: { error: 'Invalid request' }, status: :bad_request
      return
    end

    cards = CreditCard.joins(:phones)
                      .where(phones: { number: phone_numbers })
                      .group('credit_cards.id')
                      .having('COUNT(phones.id) = ?', phone_numbers.size)

    if cards.empty?
      render json: { error: 'Not found' }, status: :not_found
    else
      render json: { card_numbers: cards.pluck(:number) }, status: :ok
    end
  end

  private

  def valid_credit_card_format?(number)
    number.match?(/\A\d{16}\z/)
  end

  def valid_phone_format?(number)
    number.match?(/\A\d{1}-\d{3}-\d{3}\z/)
  end
end