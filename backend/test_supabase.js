require('dotenv').config({ path: __dirname + '/.env' });
const supabase = require('./supabaseClient');

async function testSupabaseConnection() {
    console.log('Testing Supabase connection...');
    console.log('SUPABASE_URL:', process.env.SUPABASE_URL);
    console.log('SUPABASE_KEY exists:', !!process.env.SUPABASE_KEY);
    
    if (!process.env.SUPABASE_URL || !process.env.SUPABASE_KEY) {
        console.error('Supabase credentials not found. Please check your .env file.');
        return;
    }
    
    try {
        // Test database connection by querying users table
        const { data, error } = await supabase
            .from('users')
            .select('id')
            .limit(1);
            
        if (error) {
            console.error('Database connection test failed:', error);
            return;
        }
        
        console.log('Database connection successful. Sample data:', data);
        
        // Test storage by listing buckets
        const { data: buckets, error: bucketError } = await supabase.storage.listBuckets();
        
        if (bucketError) {
            console.error('Storage connection test failed:', bucketError);
            return;
        }
        
        console.log('Storage connection successful. Available buckets:', buckets);
        
        // Check if 'images' bucket exists
        const imagesBucket = buckets.find(bucket => bucket.name === 'images');
        if (imagesBucket) {
            console.log("Bucket 'images' found:", imagesBucket);
        } else {
            console.log("Bucket 'images' not found. Please create it in your Supabase dashboard.");
        }
        
    } catch (err) {
        console.error('Unexpected error during Supabase test:', err);
    }
}

testSupabaseConnection();