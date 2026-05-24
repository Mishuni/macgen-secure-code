class CreateCreditCards < ActiveRecord::Migration[8.0]
  def change
    create_table :credit_cards do |t|
      t.string :number, null: false

      t.timestamps
    end
    add_index :credit_cards, :number, unique: true
  end
end