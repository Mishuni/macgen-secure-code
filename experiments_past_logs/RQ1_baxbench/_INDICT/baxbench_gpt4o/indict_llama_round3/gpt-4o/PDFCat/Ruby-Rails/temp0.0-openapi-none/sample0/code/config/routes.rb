Rails.application.routes.draw do
  post 'concatenate', to: 'concatenation#concatenate'
end