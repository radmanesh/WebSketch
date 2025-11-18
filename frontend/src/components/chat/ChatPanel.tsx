'use client';

import { useRef, ChangeEvent, useState, DragEvent, FormEvent, useEffect } from 'react';
import { ChatMessage } from '@/types/agent';
import { PlacedComponent } from '@/types/types';
import ChatHistory from './ChatHistory';
import ModificationPreview from './ModificationPreview';
import { agentClient } from '@/lib/api/client';

interface ChatPanelProps {
  components: PlacedComponent[];
  onModifyComponents: (modifiedSketch: PlacedComponent[]) => void;
}

export default function ChatPanel({ components, onModifyComponents }: ChatPanelProps) {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [message, setMessage] = useState('');
  const [isDragging, setIsDragging] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [pendingModification, setPendingModification] = useState<{
    modifiedSketch: PlacedComponent[];
    operations: any[];
    reasoning: string;
    description: string;
  } | null>(null);
  const [selectedImage, setSelectedImage] = useState<File | null>(null);
  const [imagePreview, setImagePreview] = useState<string | null>(null);
  const historyRef = useRef<HTMLDivElement>(null);

  // Initialize session on mount if needed
  useEffect(() => {
    if (components.length > 0 && !agentClient.getSessionId()) {
      agentClient.createSession(components).catch(err => {
        console.error('Failed to create session:', err);
      });
    }
  }, []);

  const processImageFile = (file: File) => {
    // Check if it's an image
    if (!file.type.startsWith('image/')) {
      alert('Please upload an image file.');
      return;
    }

    // Store the image file and create preview
    setSelectedImage(file);
    const reader = new FileReader();
    reader.onloadend = () => {
      setImagePreview(reader.result as string);
    };
    reader.readAsDataURL(file);
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
    if ((message.trim() || selectedImage) && !isLoading) {
      const userMessage = message.trim() || (selectedImage ? 'Analyze this image and recreate the layout' : '');
      const imageToSend = selectedImage;

      // Clear form
      setMessage('');
      setError(null);
      setPendingModification(null);
      setSelectedImage(null);
      setImagePreview(null);

      // Add user message to history with image preview
      const newUserMessage: ChatMessage = {
        role: 'user',
        content: userMessage || 'Uploaded image',
        timestamp: new Date(),
        imageUrl: imagePreview || undefined,
      };
      setMessages(prev => [...prev, newUserMessage]);

      setIsLoading(true);

      try {
        const response = await agentClient.chat({
          message: userMessage,
          currentSketch: components,
          messageHistory: messages.map(m => ({
            role: m.role,
            content: m.content,
            timestamp: m.timestamp?.toISOString(),
          })),
          sessionId: agentClient.getSessionId() || undefined,
          image: imageToSend || undefined,
        });

        // Add assistant response to history
        const assistantMessage: ChatMessage = {
          role: 'assistant',
          content: response.description,
          timestamp: new Date(),
        };
        setMessages(prev => [...prev, assistantMessage]);

        // Show preview of modification
        setPendingModification({
          modifiedSketch: response.modifiedSketch,
          operations: response.operations,
          reasoning: response.reasoning,
          description: response.description,
        });
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
      onModifyComponents(pendingModification.modifiedSketch);
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
          {selectedImage ? 'Change Image' : 'Upload Image'}
        </button>
        {selectedImage && (
          <div className="flex items-center gap-2 text-sm text-gray-600">
            <span className="truncate max-w-[100px]">{selectedImage.name}</span>
            <button
              onClick={() => {
                setSelectedImage(null);
                setImagePreview(null);
                if (fileInputRef.current) {
                  fileInputRef.current.value = '';
                }
              }}
              className="text-red-500 hover:text-red-700"
            >
              ×
            </button>
          </div>
        )}
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

