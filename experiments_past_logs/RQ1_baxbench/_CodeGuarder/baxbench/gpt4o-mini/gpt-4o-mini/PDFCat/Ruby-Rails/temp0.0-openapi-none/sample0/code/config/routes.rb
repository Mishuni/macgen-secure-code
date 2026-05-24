Rails.application.routes.draw do
  post '/concatenate', to: 'pdfs#concatenate'
end