# Center Deep - Container Architecture

## 🏗️ Container Structure

### **Minimum Required Containers: 2**

1. **center-deep** (port 8888) - Main application and web UI
2. **searxng-engine** (internal port 8080) - The actual search engine backend

### **Optional Container: 1**

3. **redis-cache** (port 6385) - Performance caching (recommended but not required)

## 📊 Why These Containers?

### **Center Deep Container**
- **Purpose**: Web interface, user management, admin panel, API
- **Required**: YES - This is the main application
- **Port**: 8888 (publicly accessible)

### **SearXNG Engine Container**  
- **Purpose**: The actual search functionality
- **Required**: YES - Center Deep currently uses SearXNG as its search backend
- **Port**: 8080 (internal only, not exposed externally)
- **Note**: This is an internal component, users don't interact with it directly

### **Redis Container**
- **Purpose**: Caching search results for better performance
- **Required**: NO - App works without it
- **Port**: 6385 (to avoid conflicts with default Redis)
- **Impact if removed**: 
  - ❌ No search result caching
  - ❌ Slightly slower response times
  - ✅ App still fully functional

## 🤔 Why Does Center Deep Need SearXNG?

Currently, Center Deep acts as an **enhanced interface** for SearXNG:
- Center Deep provides the UI, user management, and admin features
- SearXNG provides the actual search engine functionality
- This is similar to how many search applications work (frontend + backend)

Think of it like:
- **Center Deep** = The restaurant (UI, service, experience)
- **SearXNG** = The kitchen (actual search engine)
- **Redis** = The warming tray (cache for faster service)

## 🚀 Deployment Options

### Option 1: Full Setup (Recommended)
```bash
# Uses all 3 containers for best performance
docker-compose -f docker-compose.center-deep.yml up -d
```

### Option 2: Minimal Setup (2 containers only)
```bash
# Uses just Center Deep + SearXNG (no Redis)
docker-compose -f docker-compose.minimal.yml up -d
```

### Option 3: Without Redis
Simply comment out the redis-search service in docker-compose.center-deep.yml:
```yaml
  # redis-search:
  #   image: redis:7-alpine
  #   ...
```

## 📝 Important Notes

1. **SearXNG is currently REQUIRED** - Center Deep uses it as the search backend
2. **Redis is OPTIONAL** - The app handles its absence gracefully
3. **Tool servers are SEPARATE** - They run via docker-compose.tools.yml

## 🔮 Future Possibilities

To make Center Deep truly standalone (1 container), we would need to:
1. Integrate SearXNG code directly into Center Deep
2. OR build our own search engine functionality
3. This would be a significant architectural change

For now, the 2-container minimum (Center Deep + SearXNG) provides:
- Clean separation of concerns
- Easy updates to either component
- Better resource management
- Proven, stable search functionality

## 🎯 Summary

**Absolute Minimum**: 2 containers (center-deep + searxng-engine)
**Recommended**: 3 containers (add redis for better performance)
**Tool Servers**: Optional, separate deployment