// save-puzzle.js

// Mapping for safe characters
const safeCharMapping = {
    '+': 'plus',
    '-': 'minus',
    '*': 'times',
    '/': 'division',
};

/**
 * Generates a safe filename from the top cell values and operators.
 * @param {Array} topCellValues - Array of top cell values.
 * @param {Array} operators - Array of corresponding operators.
 * @returns {String} - A safe filename.
 */
function generateFilename(topCellValues, operators) {
    let filename = '';
    for (let i = 0; i < topCellValues.length; i++) {
        filename += topCellValues[i].toString();
        if (i < operators.length) {
            filename += '_' + safeCharMapping[operators[i]];
        }
    }
    return filename;
}

/**
 * Downloads the puzzle as a JSON file.
 * @param {Object} puzzle - The puzzle object to be downloaded.
 */
function downloadPuzzleAsJSON(puzzle) {
    const dataStr = JSON.stringify(puzzle);
    const blob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'puzzle.json';
    a.click();
    URL.revokeObjectURL(url);
}

// Example usage
// const filename = generateFilename([1, 2, 3], ['+', '-']);
// console.log(filename);
// downloadPuzzleAsJSON({ puzzleData: 'example' });
