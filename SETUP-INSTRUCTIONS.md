# 🚀 Database Setup Instructions

## ⚠️  CURRENT STATUS
Your application is running but **database tables are missing**. You need to run the SQL scripts in Supabase.

## 🔧 Quick Fix Steps

### 1. Go to Supabase Dashboard
- Open: https://supabase.com/dashboard/project/dvuzwahbcwxqlpaebezm
- Click **"SQL Editor"** → **"New query"**

### 2. Run Script 1 - Tables & Policies
Copy and paste this entire block, then click **RUN**:

```sql
CREATE TABLE IF NOT EXISTS public.profiles (
  id UUID REFERENCES auth.users(id) ON DELETE CASCADE PRIMARY KEY,
  email TEXT NOT NULL,
  username TEXT UNIQUE,
  full_name TEXT,
  avatar_url TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.political_parties (
  id SERIAL PRIMARY KEY,
  name TEXT NOT NULL UNIQUE,
  color_hex TEXT DEFAULT '#6B7280',
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.posters (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  title TEXT NOT NULL,
  description TEXT,
  image_url TEXT NOT NULL,
  image_filename TEXT NOT NULL,
  party_id INTEGER REFERENCES public.political_parties(id),
  uploaded_by UUID REFERENCES public.profiles(id) ON DELETE CASCADE,
  location TEXT,
  date_photographed DATE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.comments (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  poster_id UUID REFERENCES public.posters(id) ON DELETE CASCADE,
  user_id UUID REFERENCES public.profiles(id) ON DELETE CASCADE,
  content TEXT NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.ratings (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  poster_id UUID REFERENCES public.posters(id) ON DELETE CASCADE,
  user_id UUID REFERENCES public.profiles(id) ON DELETE CASCADE,
  rating INTEGER CHECK (rating >= 1 AND rating <= 5),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  UNIQUE(poster_id, user_id)
);

ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.posters ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.comments ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.ratings ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Public profiles are viewable by everyone" ON public.profiles FOR SELECT USING (true);
CREATE POLICY "Users can insert their own profile" ON public.profiles FOR INSERT WITH CHECK (auth.uid() = id);
CREATE POLICY "Users can update their own profile" ON public.profiles FOR UPDATE USING (auth.uid() = id);
CREATE POLICY "Posters are viewable by everyone" ON public.posters FOR SELECT USING (true);
CREATE POLICY "Authenticated users can insert posters" ON public.posters FOR INSERT WITH CHECK (auth.role() = 'authenticated');
CREATE POLICY "Users can update their own posters" ON public.posters FOR UPDATE USING (auth.uid() = uploaded_by);
CREATE POLICY "Users can delete their own posters" ON public.posters FOR DELETE USING (auth.uid() = uploaded_by);
CREATE POLICY "Comments are viewable by everyone" ON public.comments FOR SELECT USING (true);
CREATE POLICY "Authenticated users can insert comments" ON public.comments FOR INSERT WITH CHECK (auth.role() = 'authenticated');
CREATE POLICY "Users can update their own comments" ON public.comments FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Users can delete their own comments" ON public.comments FOR DELETE USING (auth.uid() = user_id);
CREATE POLICY "Ratings are viewable by everyone" ON public.ratings FOR SELECT USING (true);
CREATE POLICY "Authenticated users can insert ratings" ON public.ratings FOR INSERT WITH CHECK (auth.role() = 'authenticated');
CREATE POLICY "Users can update their own ratings" ON public.ratings FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Users can delete their own ratings" ON public.ratings FOR DELETE USING (auth.uid() = user_id);
```

### 3. Run Script 2 - Seed Data
Create a **new query** and run:

```sql
INSERT INTO public.political_parties (name, color_hex) VALUES
  ('Democratic Party', '#1f77b4'),
  ('Republican Party', '#d62728'),
  ('Green Party', '#2ca02c'),
  ('Libertarian Party', '#ff7f0e'),
  ('Independent', '#9467bd'),
  ('Other', '#8c564b')
ON CONFLICT (name) DO NOTHING;
```

### 4. Run Script 3 - Functions
Create a **new query** and run:

```sql
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO public.profiles (id, email, full_name, avatar_url)
  VALUES (NEW.id, NEW.email, NEW.raw_user_meta_data->>'full_name', NEW.raw_user_meta_data->>'avatar_url');
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created AFTER INSERT ON auth.users FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

CREATE OR REPLACE FUNCTION public.handle_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER handle_updated_at BEFORE UPDATE ON public.profiles FOR EACH ROW EXECUTE FUNCTION public.handle_updated_at();
CREATE TRIGGER handle_updated_at BEFORE UPDATE ON public.posters FOR EACH ROW EXECUTE FUNCTION public.handle_updated_at();
CREATE TRIGGER handle_updated_at BEFORE UPDATE ON public.comments FOR EACH ROW EXECUTE FUNCTION public.handle_updated_at();
```

### 5. Fix Existing Users (Run this LAST)
If you have existing users who signed up before running the scripts, run this:

```sql
INSERT INTO public.profiles (id, email, full_name, avatar_url)
SELECT 
    au.id,
    au.email,
    COALESCE(au.raw_user_meta_data->>'full_name', au.email) as full_name,
    au.raw_user_meta_data->>'avatar_url' as avatar_url
FROM auth.users au
LEFT JOIN public.profiles p ON au.id = p.id
WHERE p.id IS NULL;
```

## ✅ Verification
After running all scripts:
1. Go to **Database** → **Tables** in Supabase dashboard
2. You should see: `profiles`, `political_parties`, `posters`, `comments`, `ratings`
3. Check that `profiles` table has data if you have existing users

## 🎯 Then Test Again
- Go back to your app at http://localhost:3000
- Upload a poster
- Should work without "Failed to save poster" error!

## 🔍 Fixed Issues
✅ Column name mismatch (`political_party_id` → `party_id`)  
✅ Missing `image_filename` field  
✅ Color column name (`color` → `color_hex`)  

---
**After setup, delete this file!**
