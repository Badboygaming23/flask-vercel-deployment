const jwt = require('jsonwebtoken');
const { JWT_SECRET } = require('../config/config');
const supabase = require('../db');

const authenticateToken = async (req, res, next) => {
    try {
        const authHeader = req.headers['authorization'];
        const token = authHeader && authHeader.split(' ')[1];

        console.log('authenticateToken: Incoming request to:', req.originalUrl);
        console.log('authenticateToken: Incoming token:', token ? token.substring(0, 10) + '...' : 'No token');

        if (!token) {
            console.log('authenticateToken: No token provided for request to:', req.originalUrl);
            return res.status(401).json({ success: false, message: 'Access token required.' });
        }

        jwt.verify(token, JWT_SECRET, async (err, user) => {
            if (err) {
                console.error('authenticateToken: JWT verification error for request to:', req.originalUrl, 'Error:', err);
                return res.status(403).json({ success: false, message: 'Invalid or expired token. Please log in again.' });
            }
            console.log('authenticateToken: JWT verified for user:', user.email, 'ID:', user.id);

            const { data: users, error } = await supabase
                .from('users')
                .select('id, email')
                .eq('id', user.id)
                .eq('token', token);

            if (error) {
                console.error('authenticateToken: DB Error during token validation for request to:', req.originalUrl, 'Error:', error);
                return res.status(500).json({ success: false, message: 'An error occurred during token validation.' });
            }

            if (!users || users.length === 0) {
                console.log('authenticateToken: Token not found in DB or revoked for user:', user.email, 'ID:', user.id, 'Request to:', req.originalUrl);
                return res.status(403).json({ success: false, message: 'Invalid token. Please log in again.' });
            }

            const storedUser = users[0];
            req.user = { id: storedUser.id, email: storedUser.email };
            console.log('authenticateToken: Token successfully validated in DB for user:', req.user.email, 'Request to:', req.originalUrl);
            next();
        });
    } catch (err) {
        console.error('authenticateToken: Unexpected error for request to:', req.originalUrl, 'Error:', err);
        return res.status(500).json({ success: false, message: 'An unexpected error occurred during authentication.' });
    }
};

module.exports = authenticateToken;