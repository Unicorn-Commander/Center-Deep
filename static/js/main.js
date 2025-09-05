// Center Deep Main JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Theme Management
    const themeToggle = document.getElementById('theme-toggle');
    const themeCSS = document.getElementById('theme-css');
    
    // Load saved theme or default to dark
    const savedTheme = localStorage.getItem('theme') || 'dark';
    setTheme(savedTheme);
    
    if (themeToggle) {
        themeToggle.addEventListener('click', function() {
            const currentTheme = getCurrentTheme();
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
            setTheme(newTheme);
            localStorage.setItem('theme', newTheme);
        });
    }
    
    function getCurrentTheme() {
        return themeCSS.href.includes('theme-dark') ? 'dark' : 'light';
    }
    
    function setTheme(theme) {
        if (theme === 'dark') {
            themeCSS.href = '/static/css/theme-dark.css';
            if (themeToggle) themeToggle.textContent = '☀️';
        } else {
            themeCSS.href = '/static/css/theme-light.css';
            if (themeToggle) themeToggle.textContent = '🌙';
        }
    }
    
    // Search Suggestions
    const searchInputHome = document.getElementById('search-input-home');
    const suggestionsDiv = document.getElementById('search-suggestions');
    let suggestionTimeout;
    let currentSuggestionIndex = -1;
    let suggestions = [];
    
    if (searchInputHome && suggestionsDiv) {
        searchInputHome.addEventListener('input', function() {
            const query = this.value.trim();
            
            clearTimeout(suggestionTimeout);
            
            if (query.length < 2) {
                hideSuggestions();
                return;
            }
            
            suggestionTimeout = setTimeout(() => {
                fetchSuggestions(query);
            }, 300);
        });
        
        searchInputHome.addEventListener('keydown', function(e) {
            if (suggestions.length === 0) return;
            
            switch(e.key) {
                case 'ArrowDown':
                    e.preventDefault();
                    currentSuggestionIndex = Math.min(currentSuggestionIndex + 1, suggestions.length - 1);
                    updateActiveSuggestion();
                    break;
                case 'ArrowUp':
                    e.preventDefault();
                    currentSuggestionIndex = Math.max(currentSuggestionIndex - 1, -1);
                    updateActiveSuggestion();
                    break;
                case 'Enter':
                    if (currentSuggestionIndex >= 0) {
                        e.preventDefault();
                        selectSuggestion(suggestions[currentSuggestionIndex]);
                    }
                    break;
                case 'Escape':
                    hideSuggestions();
                    break;
            }
        });
        
        document.addEventListener('click', function(e) {
            if (!searchInputHome.contains(e.target) && !suggestionsDiv.contains(e.target)) {
                hideSuggestions();
            }
        });
    }
    
    function fetchSuggestions(query) {
        // Mock suggestions - in a real app, this would be an API call
        const mockSuggestions = [
            { text: query + ' news', type: 'search' },
            { text: query + ' wikipedia', type: 'search' },
            { text: query + ' definition', type: 'search' },
            { text: query + ' images', type: 'images' },
            { text: query + ' videos', type: 'videos' }
        ];
        
        // Add instant answers for common queries
        if (query.match(/^[\d\s+\-*/.()]+$/)) {
            try {
                const result = evaluateCalculation(query);
                if (result !== query) {
                    mockSuggestions.unshift({ text: result, type: 'calculator' });
                }
            } catch (e) {}
        }
        
        suggestions = mockSuggestions.slice(0, 6);
        displaySuggestions();
    }
    
    function displaySuggestions() {
        if (suggestions.length === 0) {
            hideSuggestions();
            return;
        }
        
        const html = suggestions.map((suggestion, index) => {
            const icon = getSuggestionIcon(suggestion.type);
            return `
                <div class="suggestion-item" data-index="${index}">
                    <div class="suggestion-icon">${icon}</div>
                    <div class="suggestion-text">${suggestion.text}</div>
                    <div class="suggestion-type">${suggestion.type}</div>
                </div>
            `;
        }).join('');
        
        suggestionsDiv.innerHTML = html;
        suggestionsDiv.classList.remove('hidden');
        
        // Add click handlers
        suggestionsDiv.querySelectorAll('.suggestion-item').forEach((item, index) => {
            item.addEventListener('click', () => selectSuggestion(suggestions[index]));
        });
    }
    
    function hideSuggestions() {
        suggestionsDiv.classList.add('hidden');
        currentSuggestionIndex = -1;
        suggestions = [];
    }
    
    function updateActiveSuggestion() {
        suggestionsDiv.querySelectorAll('.suggestion-item').forEach((item, index) => {
            item.classList.toggle('active', index === currentSuggestionIndex);
        });
        
        if (currentSuggestionIndex >= 0) {
            searchInputHome.value = suggestions[currentSuggestionIndex].text;
        }
    }
    
    function selectSuggestion(suggestion) {
        searchInputHome.value = suggestion.text;
        hideSuggestions();
        
        if (suggestion.type === 'calculator') {
            // For calculator results, don't submit the form
            return;
        }
        
        // Submit the search
        searchInputHome.closest('form').submit();
    }
    
    function getSuggestionIcon(type) {
        const icons = {
            'search': '🔍',
            'images': '🖼️',
            'videos': '🎥',
            'news': '📰',
            'calculator': '🧮'
        };
        return icons[type] || '🔍';
    }
    
    function evaluateCalculation(expr) {
        try {
            // Simple calculation evaluation (be careful with eval in production)
            const sanitized = expr.replace(/[^0-9+\-*/.() ]/g, '');
            const result = Function('"use strict"; return (' + sanitized + ')')();
            return `${expr} = ${result}`;
        } catch {
            return expr;
        }
    }
    // Add animation to search input on focus
    const searchInput = document.querySelector('.search-input');
    if (searchInput) {
        searchInput.addEventListener('focus', function() {
            this.parentElement.style.transform = 'scale(1.02)';
        });
        
        searchInput.addEventListener('blur', function() {
            this.parentElement.style.transform = 'scale(1)';
        });
    }
    
    // Add smooth scrolling
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth'
                });
            }
        });
    });
    
    // Add loading animation to search form
    const searchForm = document.querySelector('.search-form');
    if (searchForm) {
        searchForm.addEventListener('submit', function() {
            const button = this.querySelector('.search-button');
            button.textContent = 'Searching...';
            button.disabled = true;
        });
    }
});