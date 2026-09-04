// Test script to verify action button functionality
console.log('Testing action buttons...');

// Test A button
const btnA = document.getElementById('btn-a');
if (btnA) {
    console.log('Found A button, simulating click...');
    btnA.click();
    console.log('A button clicked');
} else {
    console.error('A button not found');
}

// Test B button
const btnB = document.getElementById('btn-b');
if (btnB) {
    console.log('Found B button, simulating click...');
    btnB.click();
    console.log('B button clicked');
} else {
    console.error('B button not found');
}

// Check if system messages were added
setTimeout(() => {
    const messages = document.querySelectorAll('.chat-message.system-message');
    console.log(`Found ${messages.length} system messages after button clicks`);
    messages.forEach((msg, index) => {
        const text = msg.querySelector('.message-text')?.textContent || msg.textContent;
        console.log(`Message ${index + 1}: ${text}`);
    });
}, 100);
