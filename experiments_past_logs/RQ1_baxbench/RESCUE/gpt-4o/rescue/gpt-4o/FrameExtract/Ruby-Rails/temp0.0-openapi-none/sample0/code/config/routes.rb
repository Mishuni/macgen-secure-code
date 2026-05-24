Rails.application.routes.draw do
  post "/extract", to: "extract#extract_frame"
end