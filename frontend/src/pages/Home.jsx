import { useState, useEffect } from 'react';
import SearchBar from '../components/SearchBar';
import StoryCard from '../components/StoryCard';
import Navbar from '../components/Navbar';

const API_BASE = import.meta.env.VITE_BACKEND_API_URL;


function Home({ stories = [], onStoryClick }) {
  const [displayStories, setDisplayStories] = useState(stories);
  const [selectedDomain, setSelectedDomain] = useState('All');
  const [isSearching, setIsSearching] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [domains, setDomains] = useState(['All']);

  // Load available domains
  useEffect(() => {
    const storyDomains = [...new Set(stories.map(story => story.domain))];
    setDomains(['All', ...storyDomains.sort()]);
  }, [stories]);

  // Update display when stories or filter changes
  useEffect(() => {
    filterStories();
  }, [stories, selectedDomain]);

  const filterStories = () => {
    let filtered = stories;
    
    if (selectedDomain !== 'All') {
      filtered = stories.filter(story => story.domain === selectedDomain);
    }
    
    setDisplayStories(filtered);
  };

const handleSearch = async (query) => {
  if (!query.trim()) {
    // Reset to original stories
    setDisplayStories(stories);
    setSearchQuery('');
    setIsSearching(false);
    return;
  }

  setSearchQuery(query);
  setIsSearching(true);

  try {
    const response = await fetch(`${API_BASE}/search-smart`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        query: query,
        discover_opportunities: true
      })
    });

    const results = await response.json();
    
    // IMPORTANT: Only show search results
    setDisplayStories(results.existing_stories || []);
    
    console.log(`🔍 Search for "${query}" returned ${results.existing_stories?.length || 0} results`);
    
  } catch (error) {
    console.error('Search failed:', error);
    setDisplayStories([]); // Show empty if search fails
  } finally {
    setIsSearching(false);
  }
};

  const handleClearSearch = () => {
    setSearchQuery('');
    setIsSearching(false);
    filterStories();
  };

  const handleDomainFilter = (domain) => {
    setSelectedDomain(domain);
    if (searchQuery) {
      // If there's an active search, clear it when changing domains
      handleClearSearch();
    }
  };

  return (
    <div className="home-page">
      <Navbar />
      <SearchBar onSearch={handleSearch} />
      
      {/* Domain Filters */}
      <div className="domain-filters">
        {domains.map(domain => (
          <button
            key={domain}
            onClick={() => handleDomainFilter(domain)}
            className={`filter-btn ${selectedDomain === domain ? 'active' : ''}`}
          >
            {domain}
          </button>
        ))}
      </div>
      
      {/* Search Status */}
      {searchQuery && (
        <div className="search-status">
          <div className="search-info">
            <span>🔍 Search results for "{searchQuery}"</span>
            <button onClick={handleClearSearch} className="clear-search">
              ✕ Clear
            </button>
          </div>
          {isSearching && (
            <div className="generating-indicator">
              🤖 Finding relevant opportunities...
            </div>
          )}
        </div>
      )}
      
      {/* Stories Display */}
      <div className="stories-feed">
        {displayStories.length > 0 ? (
          displayStories.map(story => (
            <StoryCard 
              key={story.id} 
              story={story} 
              onClick={onStoryClick}
            />
          ))
        ) : (
          <div className="no-stories">
            {searchQuery ? (
              <div>
                <h3>No opportunities found for "{searchQuery}"</h3>
                <p>Try a different search term or explore other domains</p>
              </div>
            ) : (
              <div>
                <h3>No stories in {selectedDomain}</h3>
                <p>Try selecting a different domain or search for opportunities</p>
              </div>
            )}
          </div>
        )}
      </div>
      
      {/* Results Count */}
      {displayStories.length > 0 && (
        <div className="results-count">
          Showing {displayStories.length} opportunities
          {selectedDomain !== 'All' && ` in ${selectedDomain}`}
          {searchQuery && ` for "${searchQuery}"`}
        </div>
      )}
    </div>
  );
}

export default Home;