'use client';

import { useRef, ChangeEvent, useState, DragEvent, FormEvent, useEffect } from 'react';
import { ChatMessage } from '@/types/agent';
import { PlacedComponent } from '@/types/types';
import ChatHistory from './ChatHistory';
import ModificationPreview from './ModificationPreview';
import { SketchModification as SketchModificationType } from '@/lib/agent/schemas';

interface ChatPanelProps {
  components: PlacedComponent[];
  onModifyComponents: (modification: SketchModificationType) => void;
}

export default function ChatPanel({ components, onModifyComponents }: ChatPanelProps) {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [message, setMessage] = useState('');
  const [isDragging, setIsDragging] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [pendingModification, setPendingModification] = useState<SketchModificationType | null>(null);
  const historyRef = useRef<HTMLDivElement>(null);

  const processImageFile = (file: File) => {
    // Check if it's an image
    if (!file.type.startsWith('image/')) {
      alert('Please upload an image file.');
      return;
    }

    // Download the image
    const url = URL.createObjectURL(file);
    const link = document.createElement('a');
    link.href = url;
    link.download = file.name;
    link.click();
    URL.revokeObjectURL(url);
  };

  const handleImageUpload = (e: ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    processImageFile(file);

    // Reset the input
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const handleUploadClick = () => {
    fileInputRef.current?.click();
  };

  const handleDragOver = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  };

  const handleDragLeave = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  };

  const handleDrop = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);

    const files = Array.from(e.dataTransfer.files);
    const imageFiles = files.filter(file => file.type.startsWith('image/'));

    if (imageFiles.length > 0) {
      // Process the first image file
      processImageFile(imageFiles[0]);
    } else if (files.length > 0) {
      alert('Please drop an image file.');
    }
  };

  useEffect(() => {
    // Scroll to bottom when new messages arrive
    if (historyRef.current) {
      historyRef.current.scrollTop = historyRef.current.scrollHeight;
    }
  }, [messages]);

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (message.trim() && !isLoading) {
      const userMessage = message.trim();
      setMessage('');
      setError(null);
      setPendingModification(null);

      // Add user message to history
      const newUserMessage: ChatMessage = {
        role: 'user',
        content: userMessage,
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, newUserMessage]);

      setIsLoading(true);

      try {
        const response = await fetch('/api/sketch/chat', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            message: userMessage,
            currentSketch: components,
            messageHistory: messages,
          }),
        });

        const data = await response.json();

        if (!response.ok || !data.success) {
          throw new Error(data.error || 'Failed to process request');
        }

        // Add assistant response to history
        const assistantMessage: ChatMessage = {
          role: 'assistant',
          content: data.modification.description,
          timestamp: new Date(),
        };
        setMessages(prev => [...prev, assistantMessage]);

        // Show preview of modification
        setPendingModification(data.modification);
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : 'An error occurred';
        setError(errorMessage);

        const errorMsg: ChatMessage = {
          role: 'assistant',
          content: `Error: ${errorMessage}`,
          timestamp: new Date(),
        };
        setMessages(prev => [...prev, errorMsg]);
      } finally {
        setIsLoading(false);
      }
    }
  };

  const handleAcceptModification = () => {
    if (pendingModification) {
      onModifyComponents(pendingModification);
      setPendingModification(null);
    }
  };

  const handleRejectModification = () => {
    setPendingModification(null);
  };

  return (
    <div className="flex flex-col border-t border-gray-300 bg-gray-50 h-64">
      {/* Chat History */}
      <div ref={historyRef} className="flex-1 overflow-y-auto">
        <ChatHistory messages={messages} />
        {isLoading && (
          <div className="px-4 py-2">
            <div className="text-sm text-gray-500 italic">Processing your request...</div>
          </div>
        )}
        {error && (
          <div className="px-4 py-2">
            <div className="text-sm text-red-600">{error}</div>
          </div>
        )}
      </div>

      {/* Modification Preview */}
      {pendingModification && (
        <ModificationPreview
          modification={pendingModification}
          onAccept={handleAcceptModification}
          onReject={handleRejectModification}
        />
      )}

      {/* Input Area */}
      <div
        className={`p-3 flex items-center gap-2 border-t border-gray-300 ${isDragging ? 'bg-blue-50 border-blue-400' : ''}`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept="image/*"
          onChange={handleImageUpload}
          className="hidden"
        />
        <button
          onClick={handleUploadClick}
          className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors text-sm font-medium flex-shrink-0"
          disabled={isLoading}
        >
          Upload Image
        </button>
        <form onSubmit={handleSubmit} className="flex-1 flex items-center gap-2">
          <input
            type="text"
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            placeholder="Type a message to modify the sketch..."
            className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
            disabled={isLoading}
          />
          <button
            type="submit"
            disabled={isLoading || !message.trim()}
            className="px-4 py-2 bg-gray-700 text-white rounded-lg hover:bg-gray-800 transition-colors text-sm font-medium flex-shrink-0 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isLoading ? 'Sending...' : 'Send'}
          </button>
        </form>
      </div>
    </div>
  );
}

