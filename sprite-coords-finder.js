const spriteWidth = 32;
const spriteHeight = 32;
const horizontalSpacing = 0;
const verticalSpacing = 0;

function getSpriteCoordinates(row, col) {
  const x = col * (spriteWidth + horizontalSpacing);
  const y = row * (spriteHeight + verticalSpacing);
  return {
    x: x,
    y: y,
    width: spriteWidth,
    height: spriteHeight
  };
}

// Example usage: Get coordinates for the sprite at row 2, column 3
const sprite = getSpriteCoordinates(2, 3);
console.log(sprite); // Output: {x: 96, y: 64, width: 32, height: 32}