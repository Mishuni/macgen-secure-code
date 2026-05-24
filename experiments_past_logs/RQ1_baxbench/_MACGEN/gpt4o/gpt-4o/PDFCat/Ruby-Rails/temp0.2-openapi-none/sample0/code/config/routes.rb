Rails.application.routes.draw do
  post '/concatenate', to: 'application#concatenate'
end