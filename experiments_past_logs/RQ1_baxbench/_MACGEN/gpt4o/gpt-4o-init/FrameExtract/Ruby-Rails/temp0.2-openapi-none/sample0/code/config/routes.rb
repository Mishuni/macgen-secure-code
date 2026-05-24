Rails.application.routes.draw do
  post '/extract', to: 'application#extract_frame'
end