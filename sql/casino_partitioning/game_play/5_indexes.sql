CREATE INDEX IF NOT EXISTS game_play_acco_id_round_id_idx ON game_play (acco_id, round_id);
CREATE INDEX IF NOT EXISTS game_play_play_id_idx ON game_play (play_id);
CREATE INDEX IF NOT EXISTS game_play_round_id_status_idx ON game_play (round_id, status) WHERE status::text = 'ACCEPTED'::text;
-- New on control column
CREATE INDEX IF NOT EXISTS game_play_placed_time_idx ON game_play (placed_time);