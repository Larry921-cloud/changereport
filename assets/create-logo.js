// Simple script to create a Rain logo placeholder
// You can replace this with the actual Rain logo PNG file

const fs = require('fs');
const { createCanvas } = require('canvas');

try {
    // Create a 200x80 canvas
    const canvas = createCanvas(200, 80);
    const ctx = canvas.getContext('2d');

    // Draw blue circle
    ctx.fillStyle = '#2679BD';
    ctx.beginPath();
    ctx.arc(40, 40, 30, 0, Math.PI * 2);
    ctx.fill();

    // Draw "rain" text in gray
    ctx.fillStyle = '#BBBBBB';
    ctx.font = 'bold 48px Arial';
    ctx.fillText('rain', 80, 60);

    // Save as PNG
    const buffer = canvas.toBuffer('image/png');
    fs.writeFileSync('rain-logo.png', buffer);
    console.log('Logo created successfully');
} catch (err) {
    console.log('Canvas not available, will use text-based title only');
}
