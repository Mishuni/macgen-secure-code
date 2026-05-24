Rails.application.routes.draw do
  post '/associate_card', to: 'credit_cards#associate_card'
  post '/retrieve_cards', to: 'credit_cards#retrieve_cards'
end