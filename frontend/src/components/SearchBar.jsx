import { useState } from 'react';

function SearchBar({ onSearch, placeholder = "Search problems, solutions..." }) {
  const [query, setQuery] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;
    
    setIsLoading(true);
    
    try {
        // Just call the parent's search function
        onSearch(query);
    } catch (error) {
        console.error('Search failed:', error);
    } finally {
        setIsLoading(false);
    }
    };

  return (
    <form onSubmit={handleSubmit} className="search-bar">
      <input
        type="text"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder={placeholder}
        className="search-input"
        disabled={isLoading}
      />
      <button type="submit" className="search-btn" disabled={isLoading}>
        {isLoading ? '🔍...' : '🔍'}
      </button>
    </form>
  );
}

export default SearchBar;