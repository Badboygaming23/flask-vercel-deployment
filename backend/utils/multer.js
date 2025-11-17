const multer = require('multer');
const path = require('path');
const fs = require('fs');

// Use environment-specific storage configuration
// For Supabase Storage, we'll temporarily store files in /tmp directory
// For local development, we'll also use /tmp and then upload to Supabase
const storage = multer.diskStorage({
        destination: function (req, file, cb) {
            // Use /tmp directory for all environments since we'll upload to Supabase Storage
            let uploadDir = '/tmp';
            // Ensure the /tmp directory exists
            if (!fs.existsSync(uploadDir)) {
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