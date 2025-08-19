-- Fix infinite recursion in RLS policies by simplifying them

-- Drop the problematic policy
DROP POLICY IF EXISTS "Users can view own profile or admins can view all" ON profiles;

-- Create a simple policy that allows users to view their own profile
-- We'll handle admin privileges in the application layer instead of RLS
CREATE POLICY "Users can view own profile" ON profiles
  FOR SELECT USING (auth.uid() = user_id);

-- Ensure users can update their own profiles
DROP POLICY IF EXISTS "Users can update own profile" ON profiles;
CREATE POLICY "Users can update own profile" ON profiles
  FOR UPDATE USING (auth.uid() = user_id);

-- Allow users to insert their own profile (for new user registration)
DROP POLICY IF EXISTS "Users can insert own profile" ON profiles;
CREATE POLICY "Users can insert own profile" ON profiles
  FOR INSERT WITH CHECK (auth.uid() = user_id);
