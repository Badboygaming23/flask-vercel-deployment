const multer = require('multer');
const path = require('path');
const fs = require('fs');

// Use environment-specific storage configuration
// For Vercel deployments, we'll use the /tmp directory
// For local development, we'll use the frontend/images directory
const storage = multer.diskStorage({
        destination: function (req, file, cb) {
            // Use /tmp directory for Vercel deployments, local directory for development
            let uploadDir = process.env.VERCEL ? '/tmp' : 'C:\\xampp\\htdocs\\fullstack express final backup\\fullstack\\frontend\\images';
            // Ensure the target directory exists (only for local development)
            if (!process.env.VERCEL && !fs.existsSync(uploadDir)) {
                fs.mkdirSync(uploadDir, { recursive: true });
            }
            cb(null, uploadDir);
        },
        filename: function (req, file, cb) {
            const uniqueSuffix = Date.now() + '-' + Math.round(Math.random() * 1E9);
            cb(null, file.fieldname + '-' + uniqueSuffix + path.extname(file.originalname));
        }
    });

const upload = multer({
    storage: storage,
    limits: { fileSize: 5 * 1024 * 1024 },
    fileFilter: (req, file, cb) => {
        const filetypes = /jpeg|jpg|png|gif/;
        const mimetype = filetypes.test(file.mimetype);
        const extname = filetypes.test(path.extname(file.originalname).toLowerCase());

        if (mimetype && extname) {
            return cb(null, true);
        }
        cb(new Error('Only images (jpeg, jpg, png, gif) are allowed!'));
    }
});

module.exports = upload;
