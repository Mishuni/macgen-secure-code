Rails.application.routes.draw do
  post '/concatenate', to: 'pdf#concatenate'
end