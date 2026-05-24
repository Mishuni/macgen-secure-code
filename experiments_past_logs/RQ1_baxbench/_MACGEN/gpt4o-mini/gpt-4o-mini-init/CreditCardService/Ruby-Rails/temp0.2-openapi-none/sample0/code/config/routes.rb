Rails.application.routes.draw do
  post '/associate_card', to: 'credit_card_associations#associate'
  post '/retrieve_cards', to: 'credit_card_associations#retrieve'
end