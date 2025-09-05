// LLM Model Discovery Functions

async function discoverModels(apiBase, apiKey) {
    const models = [];
    
    // Normalize API base URL
    apiBase = apiBase.replace(/\/$/, '');
    
    // Try OpenAI-compatible endpoint
    try {
        const response = await fetch(`${apiBase}/models`, {
            headers: {
                'Authorization': `Bearer ${apiKey}`,
                'Content-Type': 'application/json'
            }
        });
        
        if (response.ok) {
            const data = await response.json();
            if (data.data && Array.isArray(data.data)) {
                data.data.forEach(model => {
                    models.push({
                        id: model.id,
                        name: model.id,
                        type: detectModelType(model.id),
                        provider: detectProvider(apiBase, model.id)
                    });
                });
            }
        }
    } catch (error) {
        console.error('Failed to fetch models:', error);
    }
    
    // If no models found, return common defaults based on provider
    if (models.length === 0) {
        const provider = detectProviderFromUrl(apiBase);
        return getDefaultModels(provider);
    }
    
    return models;
}

function detectModelType(modelId) {
    const id = modelId.toLowerCase();
    
    if (id.includes('gpt') || id.includes('claude') || id.includes('llama') || id.includes('mistral')) {
        return 'llm';
    } else if (id.includes('embed') || id.includes('ada')) {
        return 'embedding';
    } else if (id.includes('rerank')) {
        return 'reranker';
    }
    
    return 'llm'; // Default
}

function detectProvider(apiBase, modelId = '') {
    const url = apiBase.toLowerCase();
    const model = modelId.toLowerCase();
    
    if (url.includes('openai') || model.includes('gpt')) {
        return 'OpenAI';
    } else if (url.includes('anthropic') || model.includes('claude')) {
        return 'Anthropic';
    } else if (url.includes('cohere')) {
        return 'Cohere';
    } else if (url.includes('huggingface')) {
        return 'HuggingFace';
    } else if (url.includes('localhost') || url.includes('127.0.0.1')) {
        return 'Local';
    }
    
    return 'Custom';
}

function detectProviderFromUrl(apiBase) {
    const url = apiBase.toLowerCase();
    
    if (url.includes('openai')) return 'openai';
    if (url.includes('anthropic')) return 'anthropic';
    if (url.includes('cohere')) return 'cohere';
    if (url.includes('huggingface')) return 'huggingface';
    if (url.includes('localhost') || url.includes('127.0.0.1')) return 'local';
    
    return 'custom';
}

function getDefaultModels(provider) {
    const defaults = {
        openai: [
            { id: 'gpt-4-turbo-preview', name: 'GPT-4 Turbo', type: 'llm', provider: 'OpenAI' },
            { id: 'gpt-4', name: 'GPT-4', type: 'llm', provider: 'OpenAI' },
            { id: 'gpt-3.5-turbo', name: 'GPT-3.5 Turbo', type: 'llm', provider: 'OpenAI' },
            { id: 'text-embedding-ada-002', name: 'Ada Embeddings v2', type: 'embedding', provider: 'OpenAI' },
            { id: 'text-embedding-3-small', name: 'Embeddings v3 Small', type: 'embedding', provider: 'OpenAI' },
            { id: 'text-embedding-3-large', name: 'Embeddings v3 Large', type: 'embedding', provider: 'OpenAI' }
        ],
        anthropic: [
            { id: 'claude-3-opus-20240229', name: 'Claude 3 Opus', type: 'llm', provider: 'Anthropic' },
            { id: 'claude-3-sonnet-20240229', name: 'Claude 3 Sonnet', type: 'llm', provider: 'Anthropic' },
            { id: 'claude-3-haiku-20240307', name: 'Claude 3 Haiku', type: 'llm', provider: 'Anthropic' },
            { id: 'claude-2.1', name: 'Claude 2.1', type: 'llm', provider: 'Anthropic' },
            { id: 'claude-instant-1.2', name: 'Claude Instant', type: 'llm', provider: 'Anthropic' }
        ],
        cohere: [
            { id: 'command', name: 'Command', type: 'llm', provider: 'Cohere' },
            { id: 'command-light', name: 'Command Light', type: 'llm', provider: 'Cohere' },
            { id: 'embed-english-v3.0', name: 'Embed English v3', type: 'embedding', provider: 'Cohere' },
            { id: 'embed-multilingual-v3.0', name: 'Embed Multilingual v3', type: 'embedding', provider: 'Cohere' },
            { id: 'rerank-english-v2.0', name: 'Rerank English v2', type: 'reranker', provider: 'Cohere' },
            { id: 'rerank-multilingual-v2.0', name: 'Rerank Multilingual v2', type: 'reranker', provider: 'Cohere' }
        ],
        local: [
            { id: 'llama-3-8b', name: 'Llama 3 8B', type: 'llm', provider: 'Local' },
            { id: 'mistral-7b', name: 'Mistral 7B', type: 'llm', provider: 'Local' },
            { id: 'nomic-embed-text', name: 'Nomic Embed', type: 'embedding', provider: 'Local' },
            { id: 'all-minilm-l6-v2', name: 'MiniLM L6 v2', type: 'embedding', provider: 'Local' }
        ],
        custom: []
    };
    
    return defaults[provider] || [];
}

// Function to populate model dropdown after API key is entered
async function populateModelDropdown(selectElement, apiBase, apiKey, modelType = 'llm') {
    // Show loading state
    selectElement.innerHTML = '<option value="">Loading models...</option>';
    selectElement.disabled = true;
    
    try {
        // Discover available models
        const models = await discoverModels(apiBase, apiKey);
        
        // Filter by model type
        const filteredModels = models.filter(m => m.type === modelType);
        
        // Clear and populate dropdown
        selectElement.innerHTML = '<option value="">Select a model</option>';
        
        if (filteredModels.length > 0) {
            filteredModels.forEach(model => {
                const option = document.createElement('option');
                option.value = model.id;
                option.textContent = model.name || model.id;
                selectElement.appendChild(option);
            });
        } else {
            // Add manual entry option
            selectElement.innerHTML = '<option value="">No models found - enter manually</option>';
        }
        
        selectElement.disabled = false;
    } catch (error) {
        console.error('Failed to populate models:', error);
        selectElement.innerHTML = '<option value="">Failed to load models</option>';
        selectElement.disabled = false;
    }
}

// Export functions for use in admin panel
window.LLMModelDiscovery = {
    discoverModels,
    populateModelDropdown,
    detectProvider,
    getDefaultModels
};