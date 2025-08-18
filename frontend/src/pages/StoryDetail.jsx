import { useState, useEffect } from 'react';
import Navbar from '../components/Navbar';
import ChatInput from '../components/ChatInput';

function StoryDetail({ story, onBack }) {
  const [enrichedStory, setEnrichedStory] = useState(null);
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(true);

  // Load enriched story when component mounts
  useEffect(() => {
    loadEnrichedStory();
  }, [story.id]);

  const loadEnrichedStory = async () => {
    try {
      const response = await fetch(`http://127.0.0.1:8000/stories/${story.id}/enriched`);
      const enriched = await response.json();
      setEnrichedStory(enriched);
    } catch (error) {
      console.error('Failed to load enriched story:', error);
      setEnrichedStory(story); // Fallback to base story
    } finally {
      setIsLoading(false);
    }
  };

  const handleSendMessage = async (message) => {
    if (!message.trim()) return;
    
    // Add user message immediately
    const userMessage = { 
      id: Date.now(), 
      text: message, 
      sender: 'user',
      timestamp: new Date().toISOString()
    };
    
    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);
    
    try {
      // Call backend chat endpoint
      const response = await fetch('http://127.0.0.1:8000/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: message,
          storyId: story.id
        })
      });
      
      const chatResponse = await response.json();
      
      // Add AI response
      const aiMessage = {
        id: Date.now() + 1,
        text: chatResponse.response,
        sender: 'assistant',
        timestamp: chatResponse.timestamp
      };
      
      setMessages(prev => [...prev, aiMessage]);
      
    } catch (error) {
      console.error('Chat failed:', error);
      
      // Fallback response
      const errorMessage = {
        id: Date.now() + 1,
        text: "Sorry, I'm having trouble responding right now. Please try again!",
        sender: 'assistant',
        timestamp: new Date().toISOString()
      };
      
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

if (isLoading) {
    return (
      <div className="story-detail">
        <Navbar showBackButton={true} onBack={onBack} title="Loading..." />
        <div className="loading-story">
          <h2>🤖 Loading</h2>
        </div>
      </div>
    );
  }

  const currentStory = enrichedStory || story;
  const enrichment = currentStory.enrichment || {};

  return (
    <div className="story-detail">
      <Navbar 
        showBackButton={true} 
        onBack={onBack}
        title={currentStory.domain}
      />
      
      <div className="story-content">
        <h1>{currentStory.title}</h1>
        
        {/* Base Story Sections */}
        <div className="story-sections">
            <section className="problem-section">
            <h2>🔴 The Opportunity</h2>
            <p>{currentStory.opportunity || currentStory.problem}</p>
            </section>

            <section className="pathway-section">  
            <h2>🛤️ Current Approaches</h2>
            <p>{currentStory.gaps || currentStory.pathway}</p>
            </section>

            <section className="solution-section">
            <h2>💡 Your Project Opportunity</h2>
            <p>{currentStory.solution}</p>
            </section>
        </div>

        {/* Enriched Content */}
        {enrichment.related_startups && (
          <section className="enriched-section">
            <h2>🚀 Startups in This Space</h2>
            <div className="startups-grid">
              {enrichment.related_startups.map((startup, index) => (
                <div key={index} className="startup-card">
                  <h3>{startup.name}</h3>
                  <p>{startup.description}</p>
                  <span className="startup-approach">{startup.approach}</span>
                </div>
              ))}
            </div>
          </section>
        )}

        {enrichment.research_papers && (
          <section className="enriched-section">
            <h2>🔬 Related Research</h2>
            <div className="research-list">
              {enrichment.research_papers.map((paper, index) => (
                <div key={index} className="research-item">
                  <h4>{paper.title}</h4>
                  <p><strong>Focus:</strong> {paper.focus}</p>
                  <p><strong>Key Findings:</strong> {paper.key_findings}</p>
                </div>
              ))}
            </div>
          </section>
        )}

        {enrichment.implementation_guide && (
          <section className="enriched-section">
            <h2>🛠️ Implementation Guide</h2>
            <ol className="implementation-steps">
              {enrichment.implementation_guide.map((step, index) => (
                <li key={index}>{step}</li>
              ))}
            </ol>
          </section>
        )}

        {/* Chat Messages */}
        <div className="chat-messages">
          {messages.map(msg => (
            <div key={msg.id} className={`message ${msg.sender}`}>
              {msg.text}
            </div>
          ))}
        </div>
      </div>

      <ChatInput onSendMessage={handleSendMessage} />
    </div>
  );
}

export default StoryDetail;