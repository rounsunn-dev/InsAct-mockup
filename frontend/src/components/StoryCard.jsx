function StoryCard({ story, onClick }) {
  return (
    <div className="story-card" onClick={() => onClick(story.id)}>
      <h3>{story.title}</h3>
      <p>{story.preview}</p>
      <span>{story.domain}</span>
    </div>
  );
}

export default StoryCard;