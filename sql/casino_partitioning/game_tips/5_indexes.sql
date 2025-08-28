CREATE INDEX IF NOT EXISTS game_tips_ext_transaction_id_idx ON game_tips (ext_transaction_id);
-- New on control column
CREATE INDEX IF NOT EXISTS game_tips_created_idx ON game_tips (created);