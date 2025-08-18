import { useState } from 'react';

function ChatInput({ onSendMessage, placeholder = "Ask about this story..." }) {
  const [message, setMessage] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (message.trim()) {
      onSendMessage(message);
      setMessage(''); // Clear after sending
    }
  };

  return (
    <form onSubmit={handleSubmit} className="chat-input">
      <input
        type="text"
        value={message}
        onChange={(e) => setMessage(e.target.value)}
        placeholder={placeholder}
        className="chat-field"
      />
      <button type="submit" className="send-btn">Send</button>
    </form>
  );
}

export default ChatInput;