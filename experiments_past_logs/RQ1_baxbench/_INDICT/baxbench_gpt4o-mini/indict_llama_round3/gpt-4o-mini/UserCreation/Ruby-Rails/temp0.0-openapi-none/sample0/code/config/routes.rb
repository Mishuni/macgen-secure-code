Rails.application.routes.draw do
  post '/invite_user', to: 'invites#invite_user'
  post '/create_user', to: 'users#create_user'
end