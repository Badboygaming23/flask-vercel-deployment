// Use the Vercel backend URL for all environments
if (typeof BASE_URL === 'undefined') {
    const BASE_URL = 'https://flask-vercel-deployment-ten.vercel.app';
    // Make BASE_URL available globally for other scripts
    window.BASE_URL = BASE_URL;
}