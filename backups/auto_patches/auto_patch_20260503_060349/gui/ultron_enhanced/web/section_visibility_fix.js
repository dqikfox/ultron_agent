/**
 * Section Visibility Diagnostic & Fix
 * Ensures all sections display properly when activated
 */

console.log('[SECTION FIX] Initializing section visibility diagnostic...');

// Wait for DOM to be fully loaded
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initSectionFix);
} else {
    initSectionFix();
}

function initSectionFix() {
    console.log('[SECTION FIX] Running diagnostic checks...');

    // Check all sections exist
    const sections = document.querySelectorAll('.section-content');
    console.log(`[SECTION FIX] Found ${sections.length} sections`);

    sections.forEach(section => {
        const id = section.id;
        const hasContent = section.innerHTML.trim().length > 0;
        const isActive = section.classList.contains('active');
        const display = window.getComputedStyle(section).display;

        console.log(`[SECTION FIX] ${id}:`, {
            hasContent,
            isActive,
            display,
            innerHTML: section.innerHTML.substring(0, 100)
        });
    });

    // Check specific problematic sections
    const llmChatSection = document.getElementById('llm-chat-section');
    if (llmChatSection) {
        console.log('[SECTION FIX] LLM Chat section found');
        console.log('[SECTION FIX] Classes:', llmChatSection.className);
        console.log('[SECTION FIX] Has llm-chat-content:', !!llmChatSection.querySelector('.llm-chat-content'));
        console.log('[SECTION FIX] Has chat-messages:', !!llmChatSection.querySelector('.chat-messages'));
    } else {
        console.error('[SECTION FIX] LLM Chat section NOT FOUND!');
    }

    // Force CSS reflow
    document.querySelectorAll('.section-content').forEach(section => {
        section.style.display = section.classList.contains('active') ? 'block' : 'none';
    });

    console.log('[SECTION FIX] Diagnostic complete');
}

// Add click handler diagnostic
document.addEventListener('click', (e) => {
    if (e.target.classList.contains('nav-button')) {
        const section = e.target.dataset.section;
        console.log(`[SECTION FIX] Nav button clicked: ${section}`);

        setTimeout(() => {
            const targetSection = document.getElementById(`${section}-section`);
            if (targetSection) {
                const isActive = targetSection.classList.contains('active');
                const display = window.getComputedStyle(targetSection).display;
                console.log(`[SECTION FIX] After switch to ${section}:`, {
                    isActive,
                    display
                });
            }
        }, 100);
    }
});
