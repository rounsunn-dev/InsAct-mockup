import { useState, useEffect } from 'react';
import Home from './pages/Home';
import StoryDetail from './pages/StoryDetail';
import { api } from './services/api';
import './index.css'

function App() {
  // Navigation state
  const [currentPage, setCurrentPage] = useState('home');
  const [selectedStoryId, setSelectedStoryId] = useState(null);
  
  // Data state
  const [stories, setStories] = useState([]);
  const [currentStory, setCurrentStory] = useState(null);

  // Load stories on app start
  useEffect(() => {
    loadStories();
  }, []);

  const loadStories = async () => {
    try {
      const data = await api.getStories();
      //const data = MOCK_STORIES;
      setStories(data);
    } catch (error) {
      console.error('Failed to load stories:', error);
    }
  };

  const handleStoryClick = async (storyId) => {
    try {
      const story = await api.getStory(storyId);
      setCurrentStory(story);
      setSelectedStoryId(storyId);
      setCurrentPage('story-detail');
    } catch (error) {
      console.error('Failed to load story:', error);
    }
  };

  const handleBack = () => {
    setCurrentPage('home');
    setCurrentStory(null);
    setSelectedStoryId(null);
  };

  const handleSendMessage = async (message, storyId) => {
    try {
      const response = await api.sendMessage(message, storyId);
      // Handle AI response (you'll implement this)
      console.log('AI Response:', response);
    } catch (error) {
      console.error('Message failed:', error);
    }
  };

  // Router logic
  if (currentPage === 'story-detail') {
    return (
      <StoryDetail
        story={currentStory}
        onBack={handleBack}
        onSendMessage={handleSendMessage}
      />
    );
  }

  return (
    <Home
      stories={stories}
      onStoryClick={handleStoryClick}
    />
  );
}

export default App;