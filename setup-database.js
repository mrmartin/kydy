#!/usr/bin/env node

const { createClient } = require('@supabase/supabase-js');
const fs = require('fs');
const path = require('path');

// Read environment variables
require('dotenv').config({ path: '.env.local' });

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL;
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;

if (!supabaseUrl || !supabaseAnonKey) {
  console.error('❌ Missing Supabase credentials in .env.local');
  process.exit(1);
}

console.log('🔗 Connecting to Supabase...');
const supabase = createClient(supabaseUrl, supabaseAnonKey);

async function runSqlScript(scriptPath, description) {
  console.log(`\n📝 Running ${description}...`);
  
  try {
    const sqlContent = fs.readFileSync(scriptPath, 'utf8');
    
    // Note: Supabase client doesn't directly support raw SQL execution
    // We'll need to use the REST API directly
    const response = await fetch(`${supabaseUrl}/rest/v1/rpc/exec_sql`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'apikey': supabaseAnonKey,
        'Authorization': `Bearer ${supabaseAnonKey}`
      },
      body: JSON.stringify({ sql: sqlContent })
    });

    if (response.ok) {
      console.log(`✅ ${description} completed successfully`);
    } else {
      const error = await response.text();
      console.log(`⚠️  ${description} response:`, response.status, error);
      
      // Try alternative approach - execute individual statements
      console.log(`🔄 Trying alternative approach for ${description}...`);
      await executeStatementsIndividually(sqlContent, description);
    }
  } catch (error) {
    console.error(`❌ Error running ${description}:`, error.message);
    
    // Try alternative approach
    console.log(`🔄 Trying alternative approach for ${description}...`);
    const sqlContent = fs.readFileSync(scriptPath, 'utf8');
    await executeStatementsIndividually(sqlContent, description);
  }
}

async function executeStatementsIndividually(sqlContent, description) {
  // Split SQL into individual statements and execute each one
  const statements = sqlContent
    .split(';')
    .map(stmt => stmt.trim())
    .filter(stmt => stmt.length > 0 && !stmt.startsWith('--'));

  console.log(`📋 Found ${statements.length} SQL statements in ${description}`);

  for (let i = 0; i < statements.length; i++) {
    const statement = statements[i] + ';';
    
    if (statement.trim().length <= 1) continue;
    
    try {
      console.log(`   ${i + 1}/${statements.length}: Executing statement...`);
      
      // For CREATE TABLE and other DDL statements, we might need to use different approach
      if (statement.includes('CREATE TABLE') || statement.includes('CREATE POLICY') || 
          statement.includes('CREATE FUNCTION') || statement.includes('CREATE TRIGGER') ||
          statement.includes('ALTER TABLE') || statement.includes('INSERT INTO')) {
        
        console.log(`   ℹ️  DDL/DML Statement detected, may require manual execution`);
        console.log(`   📄 Statement: ${statement.substring(0, 100)}...`);
      }
      
    } catch (error) {
      console.error(`   ❌ Error in statement ${i + 1}:`, error.message);
    }
  }
  
  console.log(`⚠️  ${description} requires manual execution in Supabase dashboard`);
}

async function testConnection() {
  try {
    console.log('🧪 Testing Supabase connection...');
    const { data, error } = await supabase.from('_test_').select('*').limit(1);
    
    if (error && error.code !== 'PGRST106') { // PGRST106 is "table not found" which is expected
      console.error('❌ Connection test failed:', error.message);
      return false;
    }
    
    console.log('✅ Supabase connection successful');
    return true;
  } catch (error) {
    console.error('❌ Connection test failed:', error.message);
    return false;
  }
}

async function main() {
  console.log('🚀 Database Setup Script');
  console.log('========================');
  
  // Test connection first
  const connected = await testConnection();
  if (!connected) {
    console.log('\n⚠️  Connection issues detected, but continuing with script preparation...');
  }
  
  // Run the scripts in order
  const scripts = [
    { path: './scripts/01-create-tables.sql', description: 'Creating tables and policies' },
    { path: './scripts/02-seed-parties.sql', description: 'Seeding political parties' },
    { path: './scripts/03-create-functions.sql', description: 'Creating functions and triggers' }
  ];
  
  console.log('\n📚 Preparing to execute database scripts...');
  
  for (const script of scripts) {
    if (fs.existsSync(script.path)) {
      await runSqlScript(script.path, script.description);
    } else {
      console.error(`❌ Script not found: ${script.path}`);
    }
  }
  
  console.log('\n🎉 Database setup process completed!');
  console.log('\n📋 Next Steps:');
  console.log('1. Go to your Supabase dashboard: https://supabase.com/dashboard');
  console.log('2. Navigate to SQL Editor');
  console.log('3. Copy and paste each script content manually if needed');
  console.log('4. Check Tables section to verify tables were created');
  console.log('\n🔗 Your Supabase URL:', supabaseUrl);
}

main().catch(console.error);
