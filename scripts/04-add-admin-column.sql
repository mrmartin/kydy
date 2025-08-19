-- Add admin column to profiles table
ALTER TABLE profiles ADD COLUMN admin BOOLEAN DEFAULT FALSE;

-- Update RLS policy to allow admins to view all profiles
DROP POLICY IF EXISTS "Users can view own profile" ON profiles;
CREATE POLICY "Users can view own profile or admins can view all" ON profiles
  FOR SELECT USING (
    auth.uid() = id OR 
    EXISTS (
      SELECT 1 FROM profiles 
      WHERE id = auth.uid() AND admin = true
    )
  );

-- Allow users to update their own profiles
DROP POLICY IF EXISTS "Users can update own profile" ON profiles;
CREATE POLICY "Users can update own profile" ON profiles
  FOR UPDATE USING (auth.uid() = id);
