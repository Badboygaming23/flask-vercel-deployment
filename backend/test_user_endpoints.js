require('dotenv').config({ path: __dirname + '/.env' });
const supabase = require('./supabaseClient');
const jwt = require('jsonwebtoken');
const { JWT_SECRET } = require('./config/config');

async function testUserEndpoints() {
    console.log('Testing user endpoints...');
    
    try {
        // First, let's get a user to test with
        const { data: users, error: userError } = await supabase
            .from('users')
            .select('id, email, firstname, lastname, profilepicture')
            .limit(1);
            
        if (userError) {
            console.error('Error fetching user:', userError);
            return;
        }
        
        if (!users || users.length === 0) {
            console.log('No users found in database');
            return;
        }
        
        const user = users[0];
        console.log('Testing with user:', user.email, 'ID:', user.id);
        
        // Check if the user has a local path for profile picture and update it
        if (user.profilepicture && !user.profilepicture.startsWith('http')) {
            console.log('User has local profile picture path:', user.profilepicture);
            console.log('Updating to Supabase Storage URL...');
            
            // Update the user's profile picture to use the correct Supabase Storage URL
            const { data: updateData, error: updateError } = await supabase
                .from('users')
                .update({ 
                    profilepicture: 'https://nttadnyxpbuwuhgtpvjh.supabase.co/storage/v1/object/public/images/default-profile.png' 
                })
                .eq('id', user.id);
                
            if (updateError) {
                console.error('Error updating profile picture:', updateError);
            } else {
                console.log('Profile picture updated successfully');
            }
        }
        
        // Generate a test token for this user
        const testToken = jwt.sign({ id: user.id, email: user.email }, JWT_SECRET, { expiresIn: '1h' });
        console.log('Generated test token:', testToken.substring(0, 10) + '...');
        
        // Test fetching user info (simulating the /user-info endpoint)
        console.log('\n--- Testing getUserInfo ---');
        const { data: userInfo, error: infoError } = await supabase
            .from('users')
            .select('id, firstname, middlename, lastname, email, profilepicture')
            .eq('id', user.id);
            
        if (infoError) {
            console.error('Error in getUserInfo:', infoError);
        } else if (userInfo && userInfo.length > 0) {
            const userData = userInfo[0];
            console.log('User info fetched successfully:', {
                id: userData.id,
                email: userData.email,
                firstname: userData.firstname,
                lastname: userData.lastname,
                profilePicture: userData.profilepicture
            });
        } else {
            console.log('User not found');
        }
        
        // Test fetching profile picture (simulating the /profile-picture endpoint)
        console.log('\n--- Testing getProfilePicture ---');
        const { data: profileData, error: profileError } = await supabase
            .from('users')
            .select('profilepicture')
            .eq('id', user.id);
            
        if (profileError) {
            console.error('Error in getProfilePicture:', profileError);
        } else if (profileData && profileData.length > 0) {
            let profilePicture = profileData[0].profilepicture;
            console.log('Profile picture from DB:', profilePicture);
            
            // Ensure profilePicture has a default value if null
            if (!profilePicture) {
                profilePicture = 'https://nttadnyxpbuwuhgtpvjh.supabase.co/storage/v1/object/public/images/default-profile.png';
            }
            
            console.log('Final profile picture URL:', profilePicture);
        } else {
            console.log('User not found for profile picture');
        }
        
    } catch (err) {
        console.error('Unexpected error during user endpoint test:', err);
    }
}

testUserEndpoints();