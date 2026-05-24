class CreateCreditCards < ActiveRecord::Migration[8.0]
  def change
    create_table :credit_cards do |t|
      t.string :number, null: false, unique: true

      t.timestamps
    end
  end
end