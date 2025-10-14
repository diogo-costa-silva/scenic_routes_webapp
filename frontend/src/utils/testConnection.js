/**
 * Supabase Connection Test Utility
 *
 * This file contains functions to test Supabase connection from the frontend.
 * Can be called from browser console or used in development.
 *
 * Usage:
 *   import { testSupabaseConnection } from './utils/testConnection';
 *   testSupabaseConnection();
 *
 * Or in browser console:
 *   window.testSupabaseConnection()
 */

import { supabase, fetchRoads, wktToGeoJSON } from '../services/api';

/**
 * Test basic Supabase connection and configuration
 */
export const testSupabaseConnection = async () => {
  console.log('\n🧪 Testing Supabase Connection...\n');
  console.log('='.repeat(50));

  let allPassed = true;

  // Test 1: Environment variables
  console.log('\n📋 Test 1: Environment Variables');
  const supabaseUrl = import.meta.env.VITE_SUPABASE_URL;
  const supabaseKey = import.meta.env.VITE_SUPABASE_ANON_KEY;
  const mapboxToken = import.meta.env.VITE_MAPBOX_TOKEN;

  const urlValid = Boolean(supabaseUrl?.startsWith('https://'));
  const keyValid = Boolean(supabaseKey?.length > 20);
  const mapboxValid = Boolean(mapboxToken?.startsWith('pk.'));

  console.log(`${urlValid ? '✅' : '❌'} VITE_SUPABASE_URL: ${urlValid ? supabaseUrl?.substring(0, 30) + '...' : 'Not configured'}`);
  console.log(`${keyValid ? '✅' : '❌'} VITE_SUPABASE_ANON_KEY: ${keyValid ? 'Configured (' + supabaseKey?.length + ' chars)' : 'Not configured'}`);
  console.log(`${mapboxValid ? '✅' : '❌'} VITE_MAPBOX_TOKEN: ${mapboxValid ? mapboxToken?.substring(0, 15) + '...' : 'Not configured'}`);

  if (!urlValid || !keyValid) {
    console.error('\n❌ Environment variables not properly configured!');
    console.log('   Please check your .env file in frontend/ directory');
    return false;
  }

  // Test 2: Supabase client initialization
  console.log('\n📡 Test 2: Supabase Client');
  try {
    console.log('✅ Supabase client initialized');
    console.log(`   Connected to: ${supabaseUrl}`);
  } catch (error) {
    console.error('❌ Supabase client initialization failed:', error);
    allPassed = false;
  }

  // Test 3: Fetch roads from database
  console.log('\n🗄️  Test 3: Fetch Roads from Database');
  try {
    const { data, error } = await fetchRoads();

    if (error) {
      console.error('❌ Error fetching roads:', error);
      console.log('   This may indicate:');
      console.log('   - Database schema not yet applied (run scripts/schema.sql)');
      console.log('   - RLS policies blocking access');
      console.log('   - Network connectivity issues');
      allPassed = false;
    } else if (!data || data.length === 0) {
      console.warn('⚠️  Roads table is empty');
      console.log('   Database connection works, but no data found.');
      console.log('   Run scripts/test_data.sql to add sample roads.');
    } else {
      console.log(`✅ Successfully fetched ${data.length} roads`);
      console.log('   Sample roads:');
      data.slice(0, 3).forEach(road => {
        console.log(`   - ${road.code}: ${road.name} (${road.distance_km}km)`);
      });
    }
  } catch (error) {
    console.error('❌ Fetch roads failed:', error);
    allPassed = false;
  }

  // Test 4: Test geometry conversion
  console.log('\n🗺️  Test 4: Geometry Conversion (WKT to GeoJSON)');
  try {
    const { data } = await supabase
      .from('roads')
      .select('code, geometry')
      .limit(1)
      .single();

    if (data && data.geometry) {
      const geojson = wktToGeoJSON(data.geometry);

      if (geojson && geojson.type === 'Feature') {
        console.log(`✅ WKT to GeoJSON conversion works`);
        console.log(`   Road: ${data.code}`);
        console.log(`   Geometry points: ${geojson.geometry.coordinates.length}`);
        console.log(`   Sample coordinate: [${geojson.geometry.coordinates[0].join(', ')}]`);
      } else {
        console.error('❌ Geometry conversion failed');
        allPassed = false;
      }
    } else {
      console.warn('⚠️  No geometry data to test conversion');
    }
  } catch (error) {
    console.warn('⚠️  Geometry conversion test skipped (no data)');
  }

  // Test 5: Test filtering by region
  console.log('\n🌍 Test 5: Region Filtering');
  try {
    const { data, error } = await supabase
      .from('roads')
      .select('code, region')
      .eq('region', 'Continental')
      .limit(5);

    if (error) {
      console.error('❌ Region filtering failed:', error);
      allPassed = false;
    } else {
      console.log(`✅ Region filtering works`);
      console.log(`   Found ${data?.length || 0} Continental roads`);
      if (data && data.length > 0) {
        console.log(`   Samples: ${data.map(r => r.code).join(', ')}`);
      }
    }
  } catch (error) {
    console.error('❌ Region filtering test failed:', error);
    allPassed = false;
  }

  // Summary
  console.log('\n' + '='.repeat(50));
  if (allPassed) {
    console.log('✅ All tests passed! Supabase connection is working correctly.');
    console.log('\n📝 Next steps:');
    console.log('   1. Add more roads using Python scripts');
    console.log('   2. Start building frontend components');
    console.log('   3. Test map visualization with real data');
  } else {
    console.log('❌ Some tests failed. Please review errors above.');
    console.log('\n🔧 Common fixes:');
    console.log('   1. Run schema.sql in Supabase SQL Editor');
    console.log('   2. Run test_data.sql for sample data');
    console.log('   3. Check .env file has correct credentials');
    console.log('   4. Verify Supabase RLS policies allow public read');
  }
  console.log('='.repeat(50) + '\n');

  return allPassed;
};

/**
 * Quick connection check (minimal output)
 */
export const quickConnectionCheck = async () => {
  try {
    const { data, error } = await supabase.from('roads').select('count', { count: 'exact', head: true });

    if (error) {
      console.error('❌ Connection check failed:', error.message);
      return false;
    }

    console.log('✅ Supabase connection OK');
    return true;
  } catch (error) {
    console.error('❌ Connection check failed:', error);
    return false;
  }
};

// Expose to window for console testing
if (typeof window !== 'undefined') {
  window.testSupabaseConnection = testSupabaseConnection;
  window.quickConnectionCheck = quickConnectionCheck;
}

export default testSupabaseConnection;
