# Center Deep Search Engine Configuration Guide

## Overview
Center Deep uses SearXNG as its backend search engine with an optimized configuration for best results and performance.

## Key Fixes Applied

### 1. Port Conflict Resolution
- **Issue**: Both Center Deep and SearXNG were trying to use port 8888
- **Solution**: 
  - Center Deep: Port 8888 (public interface)
  - SearXNG Backend: Port 8080 (internal only)

### 2. Search Engine Optimization
#### Enabled Search Engines:
- **Brave**: Primary search engine with full features
- **Google**: High-quality results with pagination
- **DuckDuckGo**: Privacy-focused search
- **Bing**: Microsoft's search with good coverage
- **Startpage**: Google results with privacy
- **Yandex**: International search coverage
- **Mojeek**: Independent crawler
- **Yahoo**: Additional search coverage

#### Image Search:
- Google Images, Bing Images, DuckDuckGo Images
- Brave Images, Qwant Images, Unsplash
- All with proper pagination and categorization

#### Video Search:
- YouTube, Dailymotion, Vimeo
- Brave Videos for comprehensive coverage

#### News Sources:
- Google News, Bing News, Qwant News
- Brave News for diverse perspectives

### 3. Privacy Settings Explained

#### Current Privacy Configuration:
```yaml
search:
  safe_search: 0          # 0=Off, 1=Moderate, 2=Strict
  query_in_title: false   # Prevents browser history from recording queries
  
server:
  public_instance: false  # This is a private instance
  limiter: false         # No rate limiting for private use
  
outgoing:
  useragent_suffix: "Center-Deep/1.0"  # Identifies requests as from Center Deep
```

#### Privacy Features:
- **No Query Logging**: Queries are not stored in browser titles
- **Image Proxy**: All images served through Center Deep proxy
- **No Metrics**: Disabled analytics and metrics collection
- **Private Instance**: Not listed on public instance directories

#### Basic vs Pro Privacy:
For the basic free version, current privacy settings are sufficient:
- ✅ No external analytics
- ✅ No query tracking in titles  
- ✅ Image proxy protection
- ✅ No public instance listing

Pro version could add:
- Tor proxy support
- Advanced request anonymization
- Custom headers and spoofing
- VPN integration

### 4. Performance Optimizations

#### Network Settings:
- **Request Timeout**: 8s (down from 10s) for faster responses
- **Max Timeout**: 12s (down from 15s) to prevent hanging
- **Pool Connections**: 200 (up from 100) for better concurrency
- **Pool Max Size**: 50 (up from 20) for multiple simultaneous requests
- **HTTP/2 Enabled**: For faster connections

#### Search Behavior:
- **Autocomplete**: Using Brave (more private than Google)
- **Ban Times**: Reduced to 3s initial, 60s max for faster recovery
- **Default Language**: Auto-detect instead of forcing English

### 5. Mac Networking Fix

#### Changes Made:
- Removed explicit `0.0.0.0` binding on host ports
- Added proper environment variables for SearXNG
- Fixed internal container networking
- Added searxng volume mount to main container

#### Docker Compose Changes:
```yaml
ports:
  - "8888:8888"          # Instead of "0.0.0.0:8888:8888"
  - "6385:6379"          # Instead of "0.0.0.0:6385:6379"

environment:
  - SEARXNG_BASE_URL=http://center-deep:8888/  # Internal container name
  - SEARXNG_BIND_ADDRESS=0.0.0.0              # Bind to all interfaces in container
```

## Testing the Fixes

### 1. Restart the Services
```bash
cd /Users/aaronstransky/Center-Deep
docker-compose -f docker-compose.center-deep.yml down
docker-compose -f docker-compose.center-deep.yml up -d
```

### 2. Verify Container Status
```bash
docker ps --format "table {{.Names}}\t{{.Ports}}\t{{.Status}}"
```

### 3. Test Search Functionality
- Open http://localhost:8888
- Try searches with different engines (use shortcuts like `!br query` for Brave)
- Test image, video, and news searches
- Verify results are returned properly

### 4. Check Logs if Issues Persist
```bash
docker logs center-deep-searxng-engine
docker logs center-deep
```

## Engine Shortcuts for Testing

- `!br query` - Brave Search
- `!g query` - Google
- `!dd query` - DuckDuckGo  
- `!bi query` - Bing
- `!sp query` - Startpage
- `!gi query` - Google Images
- `!yt query` - YouTube
- `!gn query` - Google News

## Monitoring Search Quality

The configuration prioritizes these engines in order:
1. Brave (privacy + quality)
2. Google (quality)
3. DuckDuckGo (privacy)
4. Bing (diversity)
5. Others as fallbacks

This ensures the best balance of privacy, quality, and comprehensive results.