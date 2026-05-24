Rails.application.routes.draw do
  post '/add_profile', to: 'profiles#create'
  get '/profile/:username', to: 'profiles#show'
  get '/profile-photo/:username', to: 'profiles#profile_photo'
end