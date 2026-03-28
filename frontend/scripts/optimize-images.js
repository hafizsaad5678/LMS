/**
 * Image Optimization Script
 * Converts PNG/JPG images to WebP format with compression
 * 
 * Usage:
 * 1. Install sharp: npm install --save-dev sharp
 * 2. Run: node scripts/optimize-images.js
 */

const sharp = require('sharp');
const fs = require('fs');
const path = require('path');

const ASSETS_DIR = path.join(__dirname, '../src/assets');
const QUALITY = 80; // WebP quality (0-100)
const MIN_SIZE_KB = 50; // Only optimize images larger than 50KB

async function optimizeImage(inputPath, outputPath) {
    try {
        const stats = fs.statSync(inputPath);
        const sizeKB = stats.size / 1024;

        if (sizeKB < MIN_SIZE_KB) {
            console.log(`⏭️  Skipping ${path.basename(inputPath)} (${sizeKB.toFixed(1)}KB - below threshold)`);
            return;
        }

        console.log(`🔄 Processing ${path.basename(inputPath)} (${sizeKB.toFixed(1)}KB)...`);

        await sharp(inputPath)
            .webp({ quality: QUALITY })
            .toFile(outputPath);

        const newStats = fs.statSync(outputPath);
        const newSizeKB = newStats.size / 1024;
        const reduction = ((sizeKB - newSizeKB) / sizeKB * 100).toFixed(1);

        console.log(`✅ Created ${path.basename(outputPath)} (${newSizeKB.toFixed(1)}KB) - ${reduction}% reduction`);
    } catch (error) {
        console.error(`❌ Error processing ${inputPath}:`, error.message);
    }
}

async function optimizeAllImages() {
    console.log('🚀 Starting image optimization...\n');

    const files = fs.readdirSync(ASSETS_DIR);
    const imageFiles = files.filter(file =>
        /\.(png|jpg|jpeg)$/i.test(file)
    );

    if (imageFiles.length === 0) {
        console.log('No images found to optimize.');
        return;
    }

    console.log(`Found ${imageFiles.length} image(s) to process:\n`);

    for (const file of imageFiles) {
        const inputPath = path.join(ASSETS_DIR, file);
        const outputPath = path.join(ASSETS_DIR, file.replace(/\.(png|jpg|jpeg)$/i, '.webp'));

        await optimizeImage(inputPath, outputPath);
    }

    console.log('\n✨ Optimization complete!');
    console.log('\n📝 Next steps:');
    console.log('1. Update image references in your Vue files to use .webp extension');
    console.log('2. Test the application to ensure images load correctly');
    console.log('3. Delete old PNG/JPG files if everything works');
}

// Run optimization
optimizeAllImages().catch(console.error);
