-- Seed political parties with their associated colors
INSERT INTO public.political_parties (name, color) VALUES
  ('Democratic Party', '#1f77b4'),
  ('Republican Party', '#d62728'),
  ('Green Party', '#2ca02c'),
  ('Libertarian Party', '#ff7f0e'),
  ('Independent', '#9467bd'),
  ('Other', '#8c564b')
ON CONFLICT (name) DO NOTHING;
