Rails.application.routes.draw do
  post '/create-gif', to: 'gif_creator#create_gif'
end