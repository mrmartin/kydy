-- Executing the party seeding script
-- Insert common political parties
INSERT INTO public.political_parties (name, color_hex) VALUES
  ('Democratic Party', '#1f77b4'),
  ('Republican Party', '#d62728'),
  ('Green Party', '#2ca02c'),
  ('Libertarian Party', '#ff7f0e'),
  ('Independent', '#9467bd'),
  ('Other', '#8c564b')
ON CONFLICT (name) DO NOTHING;
