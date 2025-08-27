#!/usr/bin/env python3
"""Update admin.html to remove blog/newsletter and add improvements"""

# Read the current admin.html
with open('/home/aaron/Development/Center-Deep/templates/admin.html', 'r') as f:
    content = f.read()

# Find the start and end positions
blog_start = content.find('        <!-- Blog Management Section -->')
tool_servers_start = content.find('        <!-- Tool Servers Section -->')

if blog_start == -1 or tool_servers_start == -1:
    print("Could not find section markers")
    exit(1)

# Create the new roadmap section
roadmap_section = '''        
        <!-- Roadmap Section -->
        <section id="roadmap" class="admin-section">
            <h2>🚀 Center Deep Roadmap</h2>
            
            <div class="admin-card">
                <h3>Coming Soon - Pro Features</h3>
                <div class="roadmap-items" style="display: grid; gap: 1rem;">
                    <div class="roadmap-item" style="padding: 1rem; background: var(--surface-color); border-radius: 8px;">
                        <h4>🤖 AI Agents & Data Scrapers</h4>
                        <p style="color: var(--text-muted); margin: 0.5rem 0;">Automated content generation and data collection from RSS feeds, GitHub, Reddit, and custom URLs.</p>
                        <span style="background: linear-gradient(45deg, #FFD700, #FFA500); color: #000; padding: 0.25rem 0.5rem; border-radius: 4px; font-size: 0.8rem; font-weight: bold;">PRO VERSION</span>
                    </div>
                    <div class="roadmap-item" style="padding: 1rem; background: var(--surface-color); border-radius: 8px;">
                        <h4>📊 Advanced Analytics</h4>
                        <p style="color: var(--text-muted); margin: 0.5rem 0;">Deep insights into search patterns, user behavior, and performance metrics.</p>
                        <span style="background: linear-gradient(45deg, #FFD700, #FFA500); color: #000; padding: 0.25rem 0.5rem; border-radius: 4px; font-size: 0.8rem; font-weight: bold;">PRO VERSION</span>
                    </div>
                    <div class="roadmap-item" style="padding: 1rem; background: var(--surface-color); border-radius: 8px;">
                        <h4>🔗 Full REST API</h4>
                        <p style="color: var(--text-muted); margin: 0.5rem 0;">Complete API for integrating Center Deep search into your applications.</p>
                        <span style="background: linear-gradient(45deg, #FFD700, #FFA500); color: #000; padding: 0.25rem 0.5rem; border-radius: 4px; font-size: 0.8rem; font-weight: bold;">PRO VERSION</span>
                    </div>
                    <div class="roadmap-item" style="padding: 1rem; background: var(--surface-color); border-radius: 8px;">
                        <h4>🎨 Custom Themes</h4>
                        <p style="color: var(--text-muted); margin: 0.5rem 0;">Create and customize your own search interface themes.</p>
                        <span style="background: var(--accent-color); color: #fff; padding: 0.25rem 0.5rem; border-radius: 4px; font-size: 0.8rem;">COMING Q2 2025</span>
                    </div>
                </div>
            </div>
            
            <div class="admin-card">
                <h3>Current Version Features</h3>
                <ul style="list-style: none; padding: 0;">
                    <li style="padding: 0.5rem 0;">✅ Privacy-first metasearch engine (replacement for SearXNG)</li>
                    <li style="padding: 0.5rem 0;">✅ Multiple search engine sources</li>
                    <li style="padding: 0.5rem 0;">✅ Tool servers for OpenWebUI integration</li>
                    <li style="padding: 0.5rem 0;">✅ LLM configuration with model discovery</li>
                    <li style="padding: 0.5rem 0;">✅ Search-optimized Redis caching</li>
                    <li style="padding: 0.5rem 0;">✅ User management system</li>
                    <li style="padding: 0.5rem 0;">✅ Customizable search settings</li>
                    <li style="padding: 0.5rem 0;">✅ Privacy mode and safe search</li>
                </ul>
            </div>
        </section>
        
'''

# Replace the content
new_content = content[:blog_start] + roadmap_section + content[tool_servers_start:]

# Write the updated file
with open('/home/aaron/Development/Center-Deep/templates/admin.html', 'w') as f:
    f.write(new_content)

print("✅ Admin template updated successfully!")
print("   - Removed blog and newsletter sections")
print("   - Removed agents section") 
print("   - Added roadmap section with Pro features")
print("   - Logo already updated to center-deep-logo.png")