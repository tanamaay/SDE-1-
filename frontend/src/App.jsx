import { useRef, useState } from "react";
import { askQuestion, getSummary, getTimestamps, toAbsoluteMediaUrl, uploadMedia } from "./services/api";
import "./App.css";

function App() {
  const [file, setFile] = useState(null);
  const [mediaId, setMediaId] = useState(null);
  const [summary, setSummary] = useState("");
  const [question, setQuestion] = useState("");
  const [chatAnswer, setChatAnswer] = useState("");
  const [chatTimestamps, setChatTimestamps] = useState([]);
  const [chatMessages, setChatMessages] = useState([]);
  const [isAsking, setIsAsking] = useState(false);
  const [topic, setTopic] = useState("");
  const [topicTimestamps, setTopicTimestamps] = useState([]);
  const [playableUrl, setPlayableUrl] = useState("");
  const [mediaUrl, setMediaUrl] = useState("");
  const [isPlayableMedia, setIsPlayableMedia] = useState(false);
  const mediaRef = useRef(null);

  const handleUpload = async () => {
    if (!file) return;
    const { data } = await uploadMedia(file);
    setMediaId(data.media_id);
    const absoluteUrl = toAbsoluteMediaUrl(data.media_url);
    setMediaUrl(absoluteUrl);
    setPlayableUrl(absoluteUrl);
    setIsPlayableMedia(Boolean(file?.type?.startsWith("audio/") || file?.type?.startsWith("video/")));
  };

  const handleSummary = async () => {
    if (!mediaId) return;
    const { data } = await getSummary(mediaId);
    setSummary(data.summary);
  };

  const handleAsk = async () => {
    if (!mediaId || !question) return;
    const userMessage = question.trim();
    if (!userMessage) return;
    setIsAsking(true);
    setChatMessages((prev) => [...prev, { role: "user", text: userMessage, timestamps: [] }]);
    const { data } = await askQuestion(mediaId, question);
    setChatAnswer(data.answer);
    setChatTimestamps(data.timestamps);
    setPlayableUrl(toAbsoluteMediaUrl(data.media_url));
    setChatMessages((prev) => [...prev, { role: "assistant", text: data.answer, timestamps: data.timestamps || [] }]);
    setQuestion("");
    setIsAsking(false);
  };

  const handleTopic = async () => {
    if (!mediaId || !topic) return;
    const { data } = await getTimestamps(mediaId, topic);
    setTopicTimestamps(data.timestamps);
    setPlayableUrl(toAbsoluteMediaUrl(data.playable_url.split("?")[0]));
  };

  const playAtTimestamp = (timestamp) => {
    if (!mediaRef.current || !isPlayableMedia) return;
    mediaRef.current.currentTime = Number(timestamp);
    mediaRef.current.play();
  };

  return (
    <div className="app-shell">
      <div className="app-gradient" />
      <div className="app-container">
        <header className="app-header">
          <h1>AI-Powered Document & Multimedia Q&A</h1>
          <p>Upload files, ask questions, get summaries, and jump to relevant timestamps instantly.</p>
        </header>

        <section className="card">
          <h2>1) Upload PDF / Audio / Video</h2>
          <div className="row">
            <input className="input-file" type="file" accept=".pdf,audio/*,video/*" onChange={(e) => setFile(e.target.files?.[0] || null)} />
            <button className="btn btn-primary" onClick={handleUpload}>Upload</button>
          </div>
          {mediaId && <p className="muted">Uploaded media ID: {mediaId}</p>}
        {isPlayableMedia && mediaUrl && (
          <div className="media-wrap">
            {file?.type?.startsWith("video/") ? (
              <video className="media-player" ref={mediaRef} src={mediaUrl} controls />
            ) : (
              <audio className="media-player" ref={mediaRef} src={mediaUrl} controls />
            )}
          </div>
        )}
        </section>

        <section className="card">
          <h2>2) Summary</h2>
          <button className="btn btn-primary" onClick={handleSummary} disabled={!mediaId}>Generate Summary</button>
          {summary && <p className="output">{summary}</p>}
        </section>

        <section className="card">
          <h2>3) Chatbot</h2>
          <div className="chat-window">
            {chatMessages.length === 0 && <p className="chat-empty">Start by asking a question about the uploaded file.</p>}
            {chatMessages.map((msg, idx) => (
              <div key={idx} className={`chat-bubble ${msg.role === "user" ? "chat-user" : "chat-assistant"}`}>
                <span className="chat-role">{msg.role === "user" ? "You" : "AI Assistant"}</span>
                <p>{msg.text}</p>
                {msg.role === "assistant" && msg.timestamps?.length > 0 && (
                  <div className="timestamp-wrap">
                    <strong>Timestamps:</strong>
                    {msg.timestamps.map((ts, tsIdx) => (
                      <button key={tsIdx} onClick={() => playAtTimestamp(ts)} className="btn btn-chip" disabled={!isPlayableMedia}>
                        Play {ts}s
                      </button>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
          <div className="row">
            <input
              className="input-text"
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter") handleAsk();
              }}
              placeholder="Ask a question..."
            />
            <button className="btn btn-primary" onClick={handleAsk} disabled={!mediaId || isAsking}>
              {isAsking ? "Thinking..." : "Ask"}
            </button>
          </div>
          {chatAnswer && <p className="output">{chatAnswer}</p>}
        {chatTimestamps.length > 0 && (
          <div className="timestamp-wrap">
            <strong>Relevant timestamps:</strong>
            {chatTimestamps.map((ts, idx) => (
              <button key={idx} onClick={() => playAtTimestamp(ts)} className="btn btn-chip" disabled={!isPlayableMedia}>
                Play {ts}s
              </button>
            ))}
          </div>
        )}
        </section>

        <section className="card">
          <h2>4) Topic Timestamps</h2>
          <div className="row">
            <input className="input-text" value={topic} onChange={(e) => setTopic(e.target.value)} placeholder="Topic name..." />
            <button className="btn btn-primary" onClick={handleTopic} disabled={!mediaId}>Find Topic</button>
          </div>
        {topicTimestamps.length > 0 && (
          <div className="timestamp-wrap">
            {topicTimestamps.map((ts, idx) => (
              <button key={idx} onClick={() => playAtTimestamp(ts)} className="btn btn-chip" disabled={!isPlayableMedia}>
                Play topic at {ts}s
              </button>
            ))}
          </div>
        )}
        </section>
      </div>
    </div>
  );
}

export default App;
