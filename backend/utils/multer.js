const multer = require('multer');
const path = require('path');
const fs = require('fs');

// Always use disk storage to save files directly to local folder
// This ensures consistent behavior across all environments
const storage = multer.diskStorage({
        destination: function (req, file, cb) {
            // Use the specified local folder path
            let uploadDir = 'C:\\xampp\\htdocs\\fullstack express final backup\\fullstack\\frontend\\images';
            // Ensure the target directory exists
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
