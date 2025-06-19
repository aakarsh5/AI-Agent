"use client";

import React, { useRef, useEffect, useState, FormEvent } from "react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";

type Message = {
  text: string;
  sender: "user" | "bot";
};

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([
    { text: "Hello!", sender: "bot" },
    { text: "Hi, I need help.", sender: "user" },
    { text: "Sure, what can I do for you?", sender: "bot" },
  ]);
  const [input, setInput] = useState("");
  const scrollRef = useRef<HTMLDivElement>(null);

  // Scroll to bottom on message update
  useEffect(() => {
    scrollRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userMessage: Message = { text: input, sender: "user" };
    const botReply: Message = {
      text: "Thank you! We'll get back to you.",
      sender: "bot",
    };

    setMessages((prev) => [...prev, userMessage, botReply]);
    setInput("");
  };

  return (
    <div className="flex flex-col  z-0">
      {/* Header */}
      <div className="p-3 border-b flex justify-center items-center">
        <h1 className="text-2xl font-bold">Guru AI</h1>
      </div>

      {/* Scrollable message area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((msg, idx) => (
          <div
            key={idx}
            className={`max-w-xs px-4 py-2 rounded-lg ${
              msg.sender === "user"
                ? "ml-auto bg-blue-100 text-right"
                : "bg-gray-100"
            }`}
          >
            {msg.text}
          </div>
        ))}
        <div ref={scrollRef} />
      </div>

      {/* Input area at bottom */}
      <div className="border-t p-5 pb-6">
        <form
          className="flex w-full items-center gap-2"
          onSubmit={handleSubmit}
        >
          <Input
            type="text"
            placeholder="Click to chat"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            className="flex-1"
          />
          <Button type="submit" variant="outline">
            Send
          </Button>
        </form>
      </div>
    </div>
  );
}
