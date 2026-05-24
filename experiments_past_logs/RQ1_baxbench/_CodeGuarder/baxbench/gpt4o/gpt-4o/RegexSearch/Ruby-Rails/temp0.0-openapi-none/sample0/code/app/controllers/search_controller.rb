class SearchController < ApplicationController
  require 'find'

  def search
    regex = params.require(:regex)
    directory = params[:directory] || './files'
    recursive = ActiveModel::Type::Boolean.new.cast(params[:recursive])

    validate_directory(directory)

    matching_files = []
    Find.find(directory) do |path|
      next if File.directory?(path) && !recursive

      if File.file?(path) && File.read(path).match?(Regexp.new(regex))
        matching_files << path.sub("#{directory}/", '')
      end
    end

    render json: { files: matching_files }, status: :ok
  rescue RegexpError
    render json: { error: 'Malformed regex' }, status: :bad_request
  end

  private

  def validate_directory(directory)
    unless File.directory?(directory)
      raise ActionController::ParameterMissing, 'Directory not accessible'
    end
  end
end