Rails.application.routes.draw do
  post '/create-gif', to: 'gif#create'
end