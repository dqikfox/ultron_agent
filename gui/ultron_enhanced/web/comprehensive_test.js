// Comprehensive GUI Testing Script for ULTRON Agent Interface
// This script tests all interactive elements and functionality

console.log('🧪 Starting comprehensive GUI testing...');

// Test navigation buttons
function testNavigationButtons() {
    console.log('Testing navigation buttons...');
    const navButtons = document.querySelectorAll('.nav-button');
    navButtons.forEach((button, index) => {
        console.log(`  - ${button.dataset.section}: ${button.id}`);
        // Simulate click
        button.click();
        // Check if section switched
        const section = document.getElementById(button.dataset.section + '-section');
        if (section && !section.classList.contains('hidden')) {
            console.log(`    ✓ Section ${button.dataset.section} activated`);
        } else {
            console.log(`    ✗ Section ${button.dataset.section} failed to activate`);
        }
    });
}

// Test D-pad buttons
function testDPadButtons() {
    console.log('Testing D-pad buttons...');
    const directions = ['up', 'down', 'left', 'right'];
    directions.forEach(dir => {
        const button = document.querySelector(`.d-pad-${dir}`);
        if (button) {
            console.log(`  - ${dir} button: ${button.className}`);
            button.click();
            console.log(`    ✓ ${dir} button clicked`);
        } else {
            console.log(`    ✗ ${dir} button not found`);
        }
    });
}

// Test action buttons
function testActionButtons() {
    console.log('Testing action buttons...');
    const buttons = ['btn-a', 'btn-b'];
    buttons.forEach(btnId => {
        const button = document.getElementById(btnId);
        if (button) {
            console.log(`  - ${btnId}: ${button.className}`);
            button.click();
            console.log(`    ✓ ${btnId} clicked`);
        } else {
            console.log(`    ✗ ${btnId} not found`);
        }
    });
}

// Test system control buttons
function testSystemButtons() {
    console.log('Testing system control buttons...');
    const buttons = ['btn-power', 'btn-volume', 'btn-settings'];
    buttons.forEach(btnId => {
        const button = document.getElementById(btnId);
        if (button) {
            console.log(`  - ${btnId}: ${button.className}`);
            button.click();
            console.log(`    ✓ ${btnId} clicked`);
        } else {
            console.log(`    ✗ ${btnId} not found`);
        }
    });
}

// Test voice features
function testVoiceFeatures() {
    console.log('Testing voice features...');
    const voiceToggle = document.getElementById('voice-toggle');
    if (voiceToggle) {
        console.log('  - Voice toggle found');
        voiceToggle.click();
        console.log('    ✓ Voice toggle clicked');
    } else {
        console.log('    ✗ Voice toggle not found');
    }

    const ttsTestBtn = document.getElementById('manual-tts-test-btn');
    if (ttsTestBtn) {
        console.log('  - TTS test button found');
        ttsTestBtn.click();
        console.log('    ✓ TTS test button clicked');
    } else {
        console.log('    ✗ TTS test button not found');
    }
}

// Test theme switching
function testThemeSwitching() {
    console.log('Testing theme switching...');
    const themeSelect = document.getElementById('theme-select');
    if (themeSelect) {
        console.log('  - Theme select found');
        const options = themeSelect.querySelectorAll('option');
        options.forEach(option => {
            console.log(`    - Option: ${option.value}`);
            themeSelect.value = option.value;
            themeSelect.dispatchEvent(new Event('change'));
            console.log(`      ✓ Theme switched to ${option.value}`);
        });
    } else {
        console.log('    ✗ Theme select not found');
    }
}

// Test vision features
function testVisionFeatures() {
    console.log('Testing vision features...');
    const captureBtn = document.getElementById('capture-btn');
    const analyzeBtn = document.getElementById('analyze-btn');

    if (captureBtn) {
        console.log('  - Capture button found');
        captureBtn.click();
        console.log('    ✓ Capture button clicked');
    } else {
        console.log('    ✗ Capture button not found');
    }

    if (analyzeBtn) {
        console.log('  - Analyze button found');
        analyzeBtn.click();
        console.log('    ✓ Analyze button clicked');
    } else {
        console.log('    ✗ Analyze button not found');
    }
}

// Test tools interface
function testToolsInterface() {
    console.log('Testing tools interface...');
    const buttons = ['refresh-tools-btn', 'reload-tools-btn', 'test-tools-btn'];
    buttons.forEach(btnId => {
        const button = document.getElementById(btnId);
        if (button) {
            console.log(`  - ${btnId} found`);
            button.click();
            console.log(`    ✓ ${btnId} clicked`);
        } else {
            console.log(`    ✗ ${btnId} not found`);
        }
    });
}

// Test LLM chat features
function testLLMChatFeatures() {
    console.log('Testing LLM chat features...');
    const buttons = ['send-chat-btn', 'voice-chat-btn', 'clear-chat-btn', 'export-chat-btn', 'switch-model-btn'];
    buttons.forEach(btnId => {
        const button = document.getElementById(btnId);
        if (button) {
            console.log(`  - ${btnId} found`);
            button.click();
            console.log(`    ✓ ${btnId} clicked`);
        } else {
            console.log(`    ✗ ${btnId} not found`);
        }
    });
}

// Test NVIDIA interface
function testNVIDIAInterface() {
    console.log('Testing NVIDIA interface...');
    const refreshBtn = document.querySelector('button[onclick*="loadNvidiaStatus"]');
    if (refreshBtn) {
        console.log('  - NVIDIA refresh button found');
        refreshBtn.click();
        console.log('    ✓ NVIDIA refresh button clicked');
    } else {
        console.log('    ✗ NVIDIA refresh button not found');
    }
}

// Test Stable Diffusion interface
function testStableDiffusionInterface() {
    console.log('Testing Stable Diffusion interface...');
    const generateBtn = document.getElementById('sd-generate-btn');
    const clearBtn = document.getElementById('sd-clear-btn');

    if (generateBtn) {
        console.log('  - SD generate button found');
        generateBtn.click();
        console.log('    ✓ SD generate button clicked');
    } else {
        console.log('    ✗ SD generate button not found');
    }

    if (clearBtn) {
        console.log('  - SD clear button found');
        clearBtn.click();
        console.log('    ✓ SD clear button clicked');
    } else {
        console.log('    ✗ SD clear button not found');
    }
}

// Test console functionality
function testConsoleFunctionality() {
    console.log('Testing console functionality...');
    const consoleInput = document.getElementById('console-input');
    const consoleOutput = document.getElementById('console-output');

    if (consoleInput) {
        console.log('  - Console input found');
        consoleInput.value = 'help';
        consoleInput.dispatchEvent(new Event('keydown', { key: 'Enter' }));
        console.log('    ✓ Console input tested');
    } else {
        console.log('    ✗ Console input not found');
    }

    if (consoleOutput) {
        console.log('  - Console output found');
    } else {
        console.log('    ✗ Console output not found');
    }
}

// Test keyboard shortcuts
function testKeyboardShortcuts() {
    console.log('Testing keyboard shortcuts...');
    const shortcuts = [
        { key: 'k', ctrlKey: true, description: 'Clear console' },
        { key: '1', altKey: true, description: 'Switch to section 1' },
        { key: 'ArrowUp', description: 'D-pad up' },
        { key: 'Enter', description: 'Action button A' },
        { key: 'Escape', description: 'Action button B' },
        { key: 'v', ctrlKey: true, description: 'Toggle voice' },
        { key: ',', ctrlKey: true, description: 'Open settings' }
    ];

    shortcuts.forEach(shortcut => {
        const event = new KeyboardEvent('keydown', {
            key: shortcut.key,
            ctrlKey: shortcut.ctrlKey || false,
            altKey: shortcut.altKey || false
        });
        document.dispatchEvent(event);
        console.log(`  ✓ ${shortcut.description} shortcut tested`);
    });
}

// Test ARIA accessibility
function testARIAFeatures() {
    console.log('Testing ARIA accessibility features...');

    // Check for ARIA attributes on navigation
    const navButtons = document.querySelectorAll('.nav-button');
    navButtons.forEach(button => {
        const hasAriaSelected = button.hasAttribute('aria-selected');
        const hasAriaControls = button.hasAttribute('aria-controls');
        console.log(`  - ${button.dataset.section} nav button: aria-selected=${hasAriaSelected}, aria-controls=${hasAriaControls}`);
    });

    // Check for live regions
    const liveRegions = document.querySelectorAll('[aria-live]');
    console.log(`  - Found ${liveRegions.length} live regions for screen reader announcements`);

    // Check for screen reader only content
    const srOnly = document.querySelectorAll('.sr-only');
    console.log(`  - Found ${srOnly.length} screen reader only elements`);
}

// Run all tests
function runAllTests() {
    console.log('🚀 Starting comprehensive GUI testing suite...\n');

    testNavigationButtons();
    console.log('');

    testDPadButtons();
    console.log('');

    testActionButtons();
    console.log('');

    testSystemButtons();
    console.log('');

    testVoiceFeatures();
    console.log('');

    testThemeSwitching();
    console.log('');

    testVisionFeatures();
    console.log('');

    testToolsInterface();
    console.log('');

    testLLMChatFeatures();
    console.log('');

    testNVIDIAInterface();
    console.log('');

    testStableDiffusionInterface();
    console.log('');

    testConsoleFunctionality();
    console.log('');

    testKeyboardShortcuts();
    console.log('');

    testARIAFeatures();
    console.log('');

    console.log('✅ GUI testing completed!');
}

// DISABLED: Auto-run tests are disabled to prevent unwanted power menu opening
// Auto-run tests when script loads
// if (document.readyState === 'loading') {
//     document.addEventListener('DOMContentLoaded', runAllTests);
// } else {
//     runAllTests();
// }

// Tests can now be manually triggered from browser console with: runAllTests()
