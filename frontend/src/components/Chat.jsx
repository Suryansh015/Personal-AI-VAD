import { useState, useRef, useEffect } from "react";
import Message from "./Message";
import Input from "./Input";
import styles from "../styles/Chat.module.css";

export default function Chat() {
  const [messages, setMessages] = useState([]);
  const [listening, setListening] = useState(false);
  const abortRef = useRef(null);
  const recognitionRef = useRef(null);
  const messagesEndRef = useRef(null);

  /* =======================
     AUTO SCROLL
  ======================= */
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  /* =======================
     TEXT TO SPEECH (TTS)
  ======================= */
  const speak = (text) => {
    speechSynthesis.cancel(); // stop previous speech
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = 1;
    utterance.pitch = 1;
    utterance.lang = "en-US";
    speechSynthesis.speak(utterance);
  };

  /* =======================
     SEND MESSAGE (STREAMING)
  ======================= */
  const sendMessage = async (text) => {
    if (!text.trim()) return;

    speechSynthesis.cancel();
    abortRef.current?.abort();

    const controller = new AbortController();
    abortRef.current = controller;

    const newMessages = [...messages, { role: "user", text }];
    setMessages(newMessages);

    const assistantMessage = { role: "assistant", text: "" };
    setMessages((msgs) => [...msgs, assistantMessage]);

    try {
      const response = await fetch("http://127.0.0.1:5000/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: text }),
        signal: controller.signal,
      });

      if (!response.ok) throw new Error("Backend error");

      const reader = response.body.getReader();
      const decoder = new TextDecoder();

      let fullText = "";

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        const clean = chunk.replaceAll("data:", "").trim();

        fullText += clean + " ";
        assistantMessage.text = fullText;
        setMessages((msgs) => [...msgs.slice(0, -1), assistantMessage]);
      }

      speak(fullText); // speak AFTER streaming completes
    } catch (err) {
      // graceful error handling
      setMessages((msgs) => [
        ...msgs,
        { role: "assistant", text: "Oops! Something went wrong. Try again." },
      ]);
    }
  };

  /* =======================
     AUTO VOICE INPUT (VAD)
  ======================= */
  useEffect(() => {
    const SpeechRecognition =
      window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) return;

    const recognition = new SpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = false;
    recognition.lang = "en-US";

    recognition.onresult = (event) => {
      const transcript =
        event.results[event.results.length - 1][0].transcript;

      speechSynthesis.cancel();
      abortRef.current?.abort();

      sendMessage(transcript);
    };

    recognition.onstart = () => setListening(true);
    recognition.onend = () => setListening(false);

    recognition.start();
    recognitionRef.current = recognition;

    return () => recognition.stop();
  }, []);

  /* =======================
     PUSH-TO-TALK CONTROLS
  ======================= */
  const startListening = () => {
    recognitionRef.current?.start();
  };
  const stopListening = () => {
    recognitionRef.current?.stop();
  };

  return (
    <div className={styles.chat}>
      <div className={styles.messages}>
        {messages.map((m, i) => (
          <Message key={i} role={m.role} text={m.text} />
        ))}
        <div ref={messagesEndRef} />
      </div>

      <Input
        onSend={sendMessage}
        onStartListening={startListening}
        onStopListening={stopListening}
        listening={listening}
      />
    </div>
  );
}
