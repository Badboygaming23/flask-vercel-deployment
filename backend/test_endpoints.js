require('dotenv').config({ path: __dirname + '/.env' });
const express = require('express');
const app = express();
const port = 3000;

// Import the fixed userController functions
const userController = require('./controllers/userController');

// Mock request and response objects for testing
const mockReq = {
    user: {
        id: 1,
        email: 'darielganzon2023@gmail.com'
    },
    params: {
        id: 1  // This should be a number, not a string
    },
    body: {
        firstname: 'Leirad',
        lastname: 'Noznag',
        email: 'darielganzon2023@gmail.com'
    }
};

const mockRes = {
    status: function(code) {
        this.statusCode = code;
        console.log(`Setting status to: ${code}`);
        return this;
    },
    json: function(data) {
        this.data = data;
        console.log(`Response Status: ${this.statusCode || 200}`);
        console.log('Response Data:', JSON.stringify(data, null, 2));
        return this;
    }
};

async function testEndpoints() {
    console.log('Testing getUserInfo endpoint...');
    await userController.getUserInfo(mockReq, mockRes);
    
    console.log('\nTesting getProfilePicture endpoint...');
    await userController.getProfilePicture(mockReq, mockRes);
    
    console.log('\nTesting updateUserInfo endpoint...');
    await userController.updateUserInfo(mockReq, mockRes);
    
    console.log('\nAll endpoint tests completed.');
}

testEndpoints();