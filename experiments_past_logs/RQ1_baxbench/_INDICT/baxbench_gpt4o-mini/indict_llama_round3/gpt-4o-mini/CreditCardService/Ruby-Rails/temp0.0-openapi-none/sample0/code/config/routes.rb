Rails.application.routes.draw do
  post '/associate_card', to: 'cards#associate_card'
  post '/retrieve_cards', to: 'cards#retrieve_card'
end