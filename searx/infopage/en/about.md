# About Center Deep

🦄 **You can't get deeper than Center Deep**

Center Deep is a privacy-focused [metasearch engine] that aggregates results from 250+ {{link('search engines', 'preferences')}} while never storing information about its users. Built on the powerful SearXNG foundation, Center Deep takes search privacy to the next level with enhanced features and a magical user experience.

## Why Choose Center Deep?

🔒 **Complete Privacy**: We don't track, store, or profile you. Your searches remain completely anonymous.

🌊 **Deep Search Results**: Access 250+ search engines simultaneously, giving you comprehensive results from across the web.

⚡ **Lightning Fast**: Optimized performance with powerful caching and intelligent result aggregation.

🦄 **Magical Experience**: Beautiful, intuitive interface designed for the modern web with smooth animations and responsive design.

🛡️ **Ad-Free & Clean**: No advertisements, no tracking scripts, no data collection - just pure search results.

## Privacy First Philosophy

- Center Deep generates zero user profiles - we don't know who you are or what you search for
- All searches are encrypted and proxied through our secure infrastructure  
- No search history is stored anywhere - each search is completely independent
- Third-party engines never see your IP address or personal information
- Open source transparency - you can verify our privacy claims in the code

## Powered by Advanced Technology

Center Deep leverages cutting-edge search technology while maintaining complete privacy:
- **Multi-engine aggregation** from 250+ sources including Google, Bing, DuckDuckGo, Yandex, and specialized engines
- **Intelligent result ranking** that combines relevance signals without compromising privacy  
- **Real-time search** with sub-second response times
- **Mobile-optimized** experience across all devices

## How do I set it as the default search engine?

SearXNG supports [OpenSearch].  For more information on changing your default
search engine, see your browser's documentation:

- [Firefox]
- [Microsoft Edge] - Behind the link, you will also find some useful instructions
  for Chrome and Safari.
- [Chromium]-based browsers only add websites that the user navigates to without
  a path.

When adding a search engine, there must be no duplicates with the same name.  If
you encounter a problem where you cannot add the search engine, you can either:

- Remove the duplicate (default name: SearXNG) or
- Contact the owner to give the instance a different name from the default.

## How does it work?

SearXNG is a fork of the well-known [searx] [metasearch engine] which was
inspired by the [Seeks project].  It provides basic privacy by mixing your
queries with searches on other platforms without storing search data.  SearXNG
can be added to your browser's search bar; moreover, it can be set as the
default search engine.

The {{link('stats page', 'stats')}} contains some useful anonymous usage
statistics about the engines used.

## How can I make it my own?

SearXNG appreciates your concern regarding logs, so take the code from the
[SearXNG sources] and run it yourself!

Add your instance to this [list of public
instances]({{get_setting('brand.public_instances')}}) to help other people
reclaim their privacy and make the internet freer.  The more decentralized the
internet is, the more freedom we have!


[SearXNG sources]: {{GIT_URL}}
[#searxng:matrix.org]: https://matrix.to/#/#searxng:matrix.org
[SearXNG docs]: {{get_setting('brand.docs_url')}}
[searx]: https://github.com/searx/searx
[metasearch engine]: https://en.wikipedia.org/wiki/Metasearch_engine
[Weblate]: https://translate.codeberg.org/projects/searxng/
[Seeks project]: https://beniz.github.io/seeks/
[OpenSearch]: https://github.com/dewitt/opensearch/blob/master/opensearch-1-1-draft-6.md
[Firefox]: https://support.mozilla.org/en-US/kb/add-or-remove-search-engine-firefox
[Microsoft Edge]: https://support.microsoft.com/en-us/help/4028574/microsoft-edge-change-the-default-search-engine
[Chromium]: https://www.chromium.org/tab-to-search
