'use client';

import { ChatMessage } from '@/types/agent';
import ChatMessageComponent from './ChatMessage';

interface ChatHistoryProps {
  messages: ChatMessage[];
}

export default function ChatHistory({ messages }: ChatHistoryProps) {
  return (
    <div className="flex-1 overflow-y-auto p-4 space-y-2">
      {messages.length === 0 ? (
        <div className="text-center text-gray-500 mt-8">
          <p>Start a conversation to modify your sketch</p>
          <p className="text-sm mt-2">Try: "Move the input field to the right" or "Make all buttons the same size"</p>
        </div>
      ) : (
        messages.map((message, index) => (
          <ChatMessageComponent key={index} message={message} />
        ))
      )}
    </div>
  );
}

