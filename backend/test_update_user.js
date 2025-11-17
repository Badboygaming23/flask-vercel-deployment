require('dotenv').config({ path: __dirname + '/.env' });
const supabase = require('./supabaseClient');

async function testUpdateUser() {
    console.log('Testing user update directly with Supabase...');
    
    try {
        const userId = 1;
        const updateData = {
            firstname: 'Leirad',
            lastname: 'Noznag',
            email: 'darielganzon2023@gmail.com'
        };
        
        console.log('Updating user with ID:', userId);
        console.log('Update data:', updateData);
        
        // Test the update directly
        const { data, error } = await supabase
            .from('users')
            .update(updateData)
            .eq('id', userId);
            
        console.log('Supabase update response:');
        console.log('Data:', data);
        console.log('Error:', error);
        
        if (error) {
            console.error('Update failed:', error);
        } else {
            console.log('Update successful');
        }
        
    } catch (err) {
        console.error('Unexpected error:', err);
    }
}

testUpdateUser();