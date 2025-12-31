import { useState } from "react";
import styles from "../styles/Input.module.css";

export default function Input({
  onSend,
  onStartListening,
  onStopListening,
  listening,
}) {
  const [text, setText] = useState("");

  const handleSend = () => {
    if (!text.trim()) return;
    onSend(text);
    setText("");
  };

  return (
    <div className={styles.inputBox}>
      <input
        value={text}
        onChange={(e) => setText(e.target.value)}
        onKeyDown={(e) => e.key === "Enter" && handleSend()}
        placeholder="Talk to your assistant..."
      />

      <button onClick={handleSend}>Send</button>

      {/* Push-to-talk */}
      <button
        onMouseDown={onStartListening}
        onMouseUp={onStopListening}
        onTouchStart={onStartListening}
        onTouchEnd={onStopListening}
      >
        {listening ? "🎤 Listening..." : "🎤 Hold to Talk"}
      </button>
    </div>
  );
}
