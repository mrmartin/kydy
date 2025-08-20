-- Fix missing profiles for existing users
-- This will create profile records for any users that don't have them yet

INSERT INTO public.profiles (id, email, full_name, avatar_url)
SELECT 
    au.id,
    au.email,
    COALESCE(au.raw_user_meta_data->>'full_name', au.email) as full_name,
    au.raw_user_meta_data->>'avatar_url' as avatar_url
FROM auth.users au
LEFT JOIN public.profiles p ON au.id = p.id
WHERE p.id IS NULL;

-- Verify the fix worked
SELECT 
    'Users in auth.users: ' || COUNT(*) as status
FROM auth.users
UNION ALL
SELECT 
    'Users in profiles: ' || COUNT(*) as status
FROM public.profiles;
