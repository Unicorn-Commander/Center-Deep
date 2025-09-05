// Center Deep Theme Switcher
// Supports Light, Dark, and Magic Unicorn themes

document.addEventListener('DOMContentLoaded', function() {
    // Theme configuration
    const themes = {
        'light': {
            name: 'Light',
            icon: '☀️',
            file: 'theme-light.css'
        },
        'dark': {
            name: 'Dark', 
            icon: '🌙',
            file: 'theme-dark.css'
        },
        'magic-unicorn': {
            name: 'Magic Unicorn',
            icon: '🦄',
            file: 'theme-magic-unicorn.css'
        }
    };
    
    // Get theme elements
    const themeCSS = document.getElementById('theme-css');
    const themeSwitcher = document.getElementById('theme-switcher');
    const themeToggle = document.getElementById('theme-toggle'); // If using a button
    
    // Initialize theme
    function initTheme() {
        // Get saved theme or default to magic-unicorn
        const savedTheme = localStorage.getItem('theme') || 'magic-unicorn';
        setTheme(savedTheme);
        
        // Update dropdown if it exists
        if (themeSwitcher) {
            themeSwitcher.value = savedTheme;
        }
    }
    
    // Set theme
    function setTheme(themeName) {
        const theme = themes[themeName];
        if (!theme) {
            console.error('Unknown theme:', themeName);
            return;
        }
        
        // Update CSS link
        if (themeCSS) {
            themeCSS.href = `/static/css/${theme.file}`;
        }
        
        // Save preference
        localStorage.setItem('theme', themeName);
        
        // Update body class for theme-specific styles
        document.body.className = document.body.className.replace(/theme-\w+/g, '');
        document.body.classList.add(`theme-${themeName}`);
        
        // Update dropdown if exists
        if (themeSwitcher) {
            themeSwitcher.value = themeName;
        }
        
        // Update toggle button if exists
        if (themeToggle) {
            themeToggle.textContent = theme.icon;
            themeToggle.title = `Current theme: ${theme.name}`;
        }
        
        // Dispatch custom event for other components
        window.dispatchEvent(new CustomEvent('themeChanged', { 
            detail: { theme: themeName } 
        }));
    }
    
    // Handle dropdown change
    if (themeSwitcher) {
        themeSwitcher.addEventListener('change', function(e) {
            setTheme(e.target.value);
        });
    }
    
    // Handle toggle button (cycles through themes)
    if (themeToggle) {
        themeToggle.addEventListener('click', function() {
            const themeNames = Object.keys(themes);
            const currentTheme = localStorage.getItem('theme') || 'dark';
            const currentIndex = themeNames.indexOf(currentTheme);
            const nextIndex = (currentIndex + 1) % themeNames.length;
            setTheme(themeNames[nextIndex]);
        });
    }
    
    // Keyboard shortcut for theme switching (Alt + T)
    document.addEventListener('keydown', function(e) {
        if (e.altKey && e.key === 't') {
            e.preventDefault();
            const themeNames = Object.keys(themes);
            const currentTheme = localStorage.getItem('theme') || 'dark';
            const currentIndex = themeNames.indexOf(currentTheme);
            const nextIndex = (currentIndex + 1) % themeNames.length;
            setTheme(themeNames[nextIndex]);
            
            // Show notification
            showThemeNotification(themes[themeNames[nextIndex]].name);
        }
    });
    
    // Show theme change notification
    function showThemeNotification(themeName) {
        // Remove existing notification
        const existing = document.querySelector('.theme-notification');
        if (existing) {
            existing.remove();
        }
        
        // Create notification
        const notification = document.createElement('div');
        notification.className = 'theme-notification';
        notification.textContent = `Theme changed to ${themeName}`;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: var(--primary);
            color: white;
            padding: 12px 20px;
            border-radius: 8px;
            box-shadow: var(--shadow-lg);
            z-index: 9999;
            animation: slideIn 0.3s ease;
        `;
        
        document.body.appendChild(notification);
        
        // Remove after 2 seconds
        setTimeout(() => {
            notification.style.animation = 'slideOut 0.3s ease';
            setTimeout(() => notification.remove(), 300);
        }, 2000);
    }
    
    // Add CSS animations for notifications
    if (!document.getElementById('theme-animations')) {
        const style = document.createElement('style');
        style.id = 'theme-animations';
        style.textContent = `
            @keyframes slideIn {
                from {
                    transform: translateX(100%);
                    opacity: 0;
                }
                to {
                    transform: translateX(0);
                    opacity: 1;
                }
            }
            @keyframes slideOut {
                from {
                    transform: translateX(0);
                    opacity: 1;
                }
                to {
                    transform: translateX(100%);
                    opacity: 0;
                }
            }
        `;
        document.head.appendChild(style);
    }
    
    // Handle system theme preference changes
    if (window.matchMedia) {
        const darkModeQuery = window.matchMedia('(prefers-color-scheme: dark)');
        
        darkModeQuery.addEventListener('change', function(e) {
            // Only auto-switch if user hasn't set a preference
            if (!localStorage.getItem('theme')) {
                setTheme(e.matches ? 'dark' : 'light');
            }
        });
        
        // Set initial theme based on system preference if no saved preference
        if (!localStorage.getItem('theme')) {
            setTheme(darkModeQuery.matches ? 'dark' : 'light');
        }
    }
    
    // Initialize on load
    initTheme();
    
    // Export functions for use in other scripts
    window.themeManager = {
        setTheme: setTheme,
        getTheme: () => localStorage.getItem('theme') || 'magic-unicorn',
        themes: themes
    };
});