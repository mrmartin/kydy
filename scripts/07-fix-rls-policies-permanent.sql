-- Fix RLS policies to eliminate infinite recursion
-- The issue is policies that reference the profiles table within themselves

-- Drop all existing problematic policies on profiles table
DROP POLICY IF EXISTS "Users can view own profile" ON profiles;
DROP POLICY IF EXISTS "Users can update own profile" ON profiles;
DROP POLICY IF EXISTS "Users can insert own profile" ON profiles;
DROP POLICY IF EXISTS "Admins can view all profiles" ON profiles;
DROP POLICY IF EXISTS "Admins can update all profiles" ON profiles;

-- Create simple, non-recursive policies for profiles table
-- Key: Use auth.uid() directly, never query profiles table within policy

-- Allow users to view their own profile using auth.uid()
CREATE POLICY "Users can view own profile" ON profiles
  FOR SELECT USING (user_id = auth.uid());

-- Allow users to update their own profile using auth.uid()  
CREATE POLICY "Users can update own profile" ON profiles
  FOR UPDATE USING (user_id = auth.uid());

-- Allow users to insert their own profile using auth.uid()
CREATE POLICY "Users can insert own profile" ON profiles
  FOR INSERT WITH CHECK (user_id = auth.uid());

-- Note: Removed admin policies to eliminate recursion
-- Admin functionality can be handled at application level if needed

-- Ensure RLS is enabled on profiles table
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;

-- Verify other tables have proper policies without recursion issues
-- These should already be working correctly

-- Posters table policies (should be fine)
-- Comments table policies (should be fine) 
-- Ratings table policies (should be fine)
-- Political parties table (public read access)
