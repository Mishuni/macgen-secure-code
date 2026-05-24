Rails.application.routes.draw do
  post '/create_cart', to: 'carts#create'
  post '/add_to_cart', to: 'carts#add'
  post '/retrieve_cart', to: 'carts#retrieve'
end