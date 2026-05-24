Rails.application.routes.draw do
  post '/associate_card', to: 'cards#associate'
  post '/retrieve_cards', to: 'cards#retrieve'
end