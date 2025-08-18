const API_BASE = 'http://127.0.0.1:8000';

export const api = {
  // Get all stories for feed
  getStories: async () => {
    const response = await fetch(`${API_BASE}/stories`);
    return response.json();
  },

  // Get single story by ID
  getStory: async (id) => {
    const response = await fetch(`${API_BASE}/stories/${id}`);
    return response.json();
  },

  // Search stories
  searchStories: async (query) => {
    const response = await fetch(`${API_BASE}/search?q=${query}`);
    return response.json();
  },

  // Send chat message
  sendMessage: async (message, storyId) => {
    const response = await fetch(`${API_BASE}/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message, storyId })
    });
    return response.json();
  }
};