Rails.application.routes.draw do
  post '/invite_user', to: 'invitations#invite_user'
  post '/create_user', to: 'invitations#create_user'
end