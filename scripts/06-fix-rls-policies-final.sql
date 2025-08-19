-- Fix RLS policies to prevent infinite recursion
-- Drop all existing policies that might cause recursion
DROP POLICY IF EXISTS "Users can view their own profile" ON profiles;
DROP POLICY IF EXISTS "Users can update their own profile" ON profiles;
DROP POLICY IF EXISTS "Admins can view all profiles" ON profiles;
DROP POLICY IF EXISTS "Admins can update all profiles" ON profiles;
DROP POLICY IF EXISTS "profiles_select_policy" ON profiles;
DROP POLICY IF EXISTS "profiles_update_policy" ON profiles;
DROP POLICY IF EXISTS "profiles_insert_policy" ON profiles;

-- Create simple, non-recursive policies for profiles
CREATE POLICY "Enable read access for users to their own profile" ON profiles
    FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Enable update for users to their own profile" ON profiles
    FOR UPDATE USING (auth.uid() = id);

CREATE POLICY "Enable insert for authenticated users" ON profiles
    FOR INSERT WITH CHECK (auth.uid() = id);

-- Ensure other tables have proper policies without recursion
DROP POLICY IF EXISTS "Users can view all posters" ON posters;
DROP POLICY IF EXISTS "Users can insert their own posters" ON posters;
DROP POLICY IF EXISTS "Users can update their own posters" ON posters;

CREATE POLICY "Enable read access for all users" ON posters
    FOR SELECT USING (true);

CREATE POLICY "Enable insert for authenticated users" ON posters
    FOR INSERT WITH CHECK (auth.uid() = uploaded_by);

CREATE POLICY "Enable update for poster owners" ON posters
    FOR UPDATE USING (auth.uid() = uploaded_by);

-- Comments policies
DROP POLICY IF EXISTS "Users can view all comments" ON comments;
DROP POLICY IF EXISTS "Users can insert their own comments" ON comments;
DROP POLICY IF EXISTS "Users can update their own comments" ON comments;

CREATE POLICY "Enable read access for all users" ON comments
    FOR SELECT USING (true);

CREATE POLICY "Enable insert for authenticated users" ON comments
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Enable update for comment owners" ON comments
    FOR UPDATE USING (auth.uid() = user_id);

-- Ratings policies
DROP POLICY IF EXISTS "Users can view all ratings" ON ratings;
DROP POLICY IF EXISTS "Users can insert their own ratings" ON ratings;
DROP POLICY IF EXISTS "Users can update their own ratings" ON ratings;

CREATE POLICY "Enable read access for all users" ON ratings
    FOR SELECT USING (true);

CREATE POLICY "Enable insert for authenticated users" ON ratings
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Enable update for rating owners" ON ratings
    FOR UPDATE USING (auth.uid() = user_id);

-- Political parties should be readable by all
DROP POLICY IF EXISTS "Enable read access for all users" ON political_parties;
CREATE POLICY "Enable read access for all users" ON political_parties
    FOR SELECT USING (true);
