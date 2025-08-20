#!/bin/bash

echo "🚀 Setting up Supabase Database Schema"
echo "======================================"

# Load environment variables
source .env.local 2>/dev/null || true

if [ -z "$NEXT_PUBLIC_SUPABASE_URL" ]; then
    echo "❌ NEXT_PUBLIC_SUPABASE_URL not found in .env.local"
    exit 1
fi

# Extract database details from Supabase URL
SUPABASE_PROJECT_ID=$(echo $NEXT_PUBLIC_SUPABASE_URL | sed 's/.*:\/\/\([^.]*\).*/\1/')
echo "📊 Project ID: $SUPABASE_PROJECT_ID"

# Try to execute SQL using curl
echo ""
echo "📝 Attempting to execute SQL scripts..."

for script in scripts/01-create-tables.sql scripts/02-seed-parties.sql scripts/03-create-functions.sql; do
    if [ -f "$script" ]; then
        echo ""
        echo "📄 Processing $script..."
        
        # Read SQL content
        SQL_CONTENT=$(cat "$script")
        
        # Try to execute via Supabase API
        RESPONSE=$(curl -s -X POST \
            "${NEXT_PUBLIC_SUPABASE_URL}/rest/v1/rpc/exec_sql" \
            -H "apikey: ${NEXT_PUBLIC_SUPABASE_ANON_KEY}" \
            -H "Authorization: Bearer ${NEXT_PUBLIC_SUPABASE_ANON_KEY}" \
            -H "Content-Type: application/json" \
            -d "{\"sql\": $(echo "$SQL_CONTENT" | jq -R -s .)}")
        
        echo "📤 Response: $RESPONSE"
        
        # Check if response contains error
        if echo "$RESPONSE" | grep -q "error\|PGRST"; then
            echo "⚠️  API execution failed for $script"
        else
            echo "✅ $script may have executed successfully"
        fi
    else
        echo "❌ Script $script not found"
    fi
done

echo ""
echo "🎯 Manual Execution Required"
echo "============================"
echo ""
echo "The automatic execution may not have worked completely."
echo "Please manually execute the following scripts in your Supabase dashboard:"
echo ""
echo "1. Go to: https://supabase.com/dashboard/project/$SUPABASE_PROJECT_ID"
echo "2. Click 'SQL Editor' in the sidebar"
echo "3. Copy and paste each script below:"
echo ""

echo "📄 SCRIPT 1 - Create Tables (01-create-tables.sql):"
echo "======================================================"
cat scripts/01-create-tables.sql
echo ""

echo "📄 SCRIPT 2 - Seed Parties (02-seed-parties.sql):"
echo "=================================================="
cat scripts/02-seed-parties.sql
echo ""

echo "📄 SCRIPT 3 - Create Functions (03-create-functions.sql):"
echo "========================================================"
cat scripts/03-create-functions.sql
echo ""

echo "🎉 After running these scripts manually, your database will be ready!"
echo "💡 Then test the poster upload functionality again."
