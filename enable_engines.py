#!/usr/bin/env python3
# Enable the main search engines in Center Deep

import yaml

settings_file = '/Users/aaronstransky/Center-Deep/searx/settings.yml'

# Engines we want to enable (the main ones)
engines_to_enable = [
    'google',
    'duckduckgo', 
    'brave',
    'startpage',
    'qwant',
    'bing',  # Even though user doesn't like it, we'll rank it lower
    'wikipedia',
    'github',
    'stackoverflow'
]

with open(settings_file, 'r') as f:
    settings = yaml.safe_load(f)

# Enable the specified engines
for engine in settings.get('engines', []):
    if engine.get('name') in engines_to_enable:
        if 'disabled' in engine:
            del engine['disabled']
        print(f"✅ Enabled: {engine.get('name')}")
    elif engine.get('name') and not engine.get('disabled'):
        # Keep other already enabled engines
        print(f"📌 Already enabled: {engine.get('name')}")

# Save the updated settings
with open(settings_file, 'w') as f:
    yaml.dump(settings, f, default_flow_style=False, sort_keys=False)

print("\n🎯 Settings updated successfully!")
