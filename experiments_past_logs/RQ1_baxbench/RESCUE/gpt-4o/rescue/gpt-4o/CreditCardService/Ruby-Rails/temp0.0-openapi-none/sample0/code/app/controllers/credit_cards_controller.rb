class CreditCardsController < ApplicationController
  def associate_card
    credit_card = CreditCard.find_or_create_by!(number: params[:credit_card])
    phone = Phone.find_or_create_by!(number: params[:phone])

    credit_card.phones << phone unless credit_card.phones.include?(phone)

    render json: { message: 'Association created successfully' }, status: :created
  end

  def retrieve_cards
    phone_numbers = params[:phone_numbers]
    if phone_numbers.blank? || !phone_numbers.is_a?(Array)
      render json: { error: 'Invalid request: phone_numbers must be an array' }, status: :bad_request
      return
    end

    phones = Phone.where(number: phone_numbers)
    if phones.size != phone_numbers.size
      render json: { error: 'Not all phone numbers found' }, status: :not_found
      return
    end

    credit_cards = CreditCard.joins(:phones)
                             .where(phones: { id: phones.pluck(:id) })
                             .group('credit_cards.id')
                             .having('COUNT(phones.id) = ?', phone_numbers.size)

    render json: { card_numbers: credit_cards.pluck(:number) }, status: :ok
  end
end