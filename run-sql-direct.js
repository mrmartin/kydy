#!/usr/bin/env node

const fs = require('fs');
const https = require('https');

// Read environment variables
require('dotenv').config({ path: '.env.local' });

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL;
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;

function executeSQL(sql, description) {
  return new Promise((resolve, reject) => {
    const url = new URL('/rest/v1/rpc/exec_sql', supabaseUrl);
    
    const postData = JSON.stringify({ sql: sql });
    
    const options = {
      hostname: url.hostname,
      port: 443,
      path: url.pathname,
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'apikey': supabaseAnonKey,
        'Authorization': `Bearer ${supabaseAnonKey}`,
        'Content-Length': Buffer.byteLength(postData)
      }
    };

    const req = https.request(options, (res) => {
      let data = '';
      
      res.on('data', (chunk) => {
        data += chunk;
      });
      
      res.on('end', () => {
        if (res.statusCode === 200) {
          console.log(`✅ ${description} executed successfully`);
          resolve(data);
        } else {
          console.log(`⚠️  ${description} returned status ${res.statusCode}`);
          console.log(`📄 Response: ${data}`);
          resolve(data); // Don't reject, just continue
        }
      });
    });

    req.on('error', (error) => {
      console.error(`❌ Error executing ${description}:`, error.message);
      resolve(null); // Don't reject, just continue
    });

    req.write(postData);
    req.end();
  });
}

async function runScript(scriptPath, description) {
  console.log(`\n📝 Executing ${description}...`);
  
  try {
    const sqlContent = fs.readFileSync(scriptPath, 'utf8');
    
    // Clean up the SQL - remove comments and split into statements
    const statements = sqlContent
      .split('\n')
      .filter(line => !line.trim().startsWith('--') && line.trim().length > 0)
      .join('\n')
      .split(';')
      .map(stmt => stmt.trim())
      .filter(stmt => stmt.length > 0);

    console.log(`📋 Found ${statements.length} statements to execute`);

    for (let i = 0; i < statements.length; i++) {
      const statement = statements[i] + ';';
      console.log(`   ${i + 1}/${statements.length}: ${statement.substring(0, 50)}...`);
      
      await executeSQL(statement, `Statement ${i + 1}`);
      
      // Small delay between statements
      await new Promise(resolve => setTimeout(resolve, 100));
    }
    
  } catch (error) {
    console.error(`❌ Error reading ${scriptPath}:`, error.message);
  }
}

async function main() {
  console.log('🚀 Direct SQL Execution Attempt');
  console.log('================================');
  
  const scripts = [
    { path: './scripts/01-create-tables.sql', description: 'Creating tables and policies' },
    { path: './scripts/02-seed-parties.sql', description: 'Seeding political parties' },
    { path: './scripts/03-create-functions.sql', description: 'Creating functions and triggers' }
  ];
  
  for (const script of scripts) {
    if (fs.existsSync(script.path)) {
      await runScript(script.path, script.description);
    } else {
      console.error(`❌ Script not found: ${script.path}`);
    }
  }
  
  console.log('\n✨ Script execution completed');
  console.log('\n🔍 Please check your Supabase dashboard to verify tables were created');
}

main().catch(console.error);
