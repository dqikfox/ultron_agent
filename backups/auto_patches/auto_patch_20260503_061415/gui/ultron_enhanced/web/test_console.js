// Test script to verify console functionality
console.log('Testing console functionality...');

// Test help command
console.log('Testing help command...');
if (window.ultronInterface && window.ultronInterface.handleConsoleCommand) {
    window.ultronInterface.handleConsoleCommand('help');
    console.log('Help command executed');
} else {
    console.error('Ultron interface not available');
}

// Test status command
setTimeout(() => {
    console.log('Testing status command...');
    if (window.ultronInterface && window.ultronInterface.handleConsoleCommand) {
        window.ultronInterface.handleConsoleCommand('status');
        console.log('Status command executed');
    }
}, 500);

// Test clear command
setTimeout(() => {
    console.log('Testing clear command...');
    if (window.ultronInterface && window.ultronInterface.handleConsoleCommand) {
        window.ultronInterface.handleConsoleCommand('clear');
        console.log('Clear command executed');
    }
}, 1000);

// Check console output after commands
setTimeout(() => {
    const output = document.getElementById('console-output');
    if (output) {
        console.log('Console output element found');
        console.log('Console output content length:', output.innerHTML.length);
        console.log('Console output has content:', output.innerHTML.trim().length > 0);
    } else {
        console.error('Console output element not found');
    }
}, 1500);
