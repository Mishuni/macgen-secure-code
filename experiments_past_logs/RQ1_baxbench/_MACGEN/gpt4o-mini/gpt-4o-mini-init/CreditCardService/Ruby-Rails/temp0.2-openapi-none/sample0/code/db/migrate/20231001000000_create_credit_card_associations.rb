class CreateCreditCardAssociations < ActiveRecord::Migration[7.0]
  def change
    create_table :credit_card_associations do |t|
      t.string :credit_card, null: false
      t.string :phone, null: false

      t.timestamps
    end
  end
end