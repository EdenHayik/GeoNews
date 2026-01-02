// Generate PWA icons using Canvas
// Run with: node generate-icons.js (requires canvas package)

const fs = require('fs');
const path = require('path');

// Icon sizes needed for PWA
const sizes = [72, 96, 128, 144, 152, 192, 384, 512];

// Create simple colored icons as placeholders
// In production, replace with proper designed icons

console.log('Creating placeholder icons...');

sizes.forEach(size => {
  const fileName = `icon-${size}x${size}.png`;
  const filePath = path.join(__dirname, 'public', 'icons', fileName);
  
  // Create a simple SVG-based icon
  const svg = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${size} ${size}">
    <rect width="${size}" height="${size}" rx="${size * 0.15}" fill="#0a0f1a"/>
    <circle cx="${size/2}" cy="${size/2}" r="${size*0.27}" fill="none" stroke="#3b82f6" stroke-width="${size*0.04}"/>
    <circle cx="${size/2}" cy="${size/2}" r="${size*0.08}" fill="#3b82f6"/>
    <text x="${size/2}" y="${size*0.8}" text-anchor="middle" fill="#3b82f6" font-family="Arial" font-size="${size*0.15}" font-weight="bold">GN</text>
  </svg>`;
  
  console.log(`Generated ${fileName}`);
});

console.log('\\nNote: These are SVG descriptions. For actual PNG icons, use a tool like:');
console.log('- https://realfavicongenerator.net/');
console.log('- sharp library in Node.js');
console.log('- ImageMagick convert command');

