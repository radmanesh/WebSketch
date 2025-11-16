'use client';

import { ChatMessage as ChatMessageType } from '@/types/agent';

interface ChatMessageProps {
  message: ChatMessageType;
}

export default function ChatMessage({ message }: ChatMessageProps) {
  const isUser = message.role === 'user';
  const isAssistant = message.role === 'assistant';

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}>
      <div
        className={`max-w-[80%] rounded-lg px-4 py-2 ${
          isUser
            ? 'bg-blue-500 text-white'
            : isAssistant
            ? 'bg-gray-200 text-gray-800'
            : 'bg-gray-100 text-gray-600 text-sm'
        }`}
      >
        <div className="whitespace-pre-wrap break-words">{message.content}</div>
        {message.timestamp && (
          <div className={`text-xs mt-1 ${isUser ? 'text-blue-100' : 'text-gray-500'}`}>
            {message.timestamp.toLocaleTimeString()}
          </div>
        )}
      </div>
    </div>
  );
}

