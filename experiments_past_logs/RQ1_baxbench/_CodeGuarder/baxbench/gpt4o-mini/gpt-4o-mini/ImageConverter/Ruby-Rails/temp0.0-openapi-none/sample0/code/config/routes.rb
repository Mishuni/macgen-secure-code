Rails.application.routes.draw do
  post '/create-gif', to: 'gifs#create'
end