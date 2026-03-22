function savePuzzle() {
    const topLeftCages = "Cage1,Cage2"; // Example cages, replace with actual data
    const fileName = topLeftCages
        .replace(/+/g, 'p') // Replace + with p
        .replace(/-/g, 'm')    // Replace - with m
        .replace(/×/g, 'x')    // Replace × with x
        .replace(/÷/g, 'd');   // Replace ÷ with d

    const puzzleData = { /* Your puzzle data here */ };
    const blob = new Blob([JSON.stringify(puzzleData, null, 2)], { type: 'application/json' });
    const link = document.createElement('a');
    link.href = window.URL.createObjectURL(blob);
    link.download = `${fileName}.json`;
    link.click();
}
