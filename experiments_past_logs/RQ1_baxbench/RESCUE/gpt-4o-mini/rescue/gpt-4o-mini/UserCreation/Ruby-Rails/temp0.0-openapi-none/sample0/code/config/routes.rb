Rails.application.routes.draw do
  post '/invite_user', to: 'users#invite_user'
  post '/create_user', to: 'users#create_user'
end