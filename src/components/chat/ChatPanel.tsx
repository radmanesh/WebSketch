'use client';

import { useRef, ChangeEvent, useState, DragEvent, FormEvent } from 'react';

export default function ChatPanel() {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [message, setMessage] = useState('');
  const [isDragging, setIsDragging] = useState(false);

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

  const handleSubmit = (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (message.trim()) {
      // For now, just clear the message
      // TODO: Handle chat message submission
      console.log('Message:', message);
      setMessage('');
    }
  };

  return (
    <div
      className={`border-t border-gray-300 bg-gray-50 p-3 flex items-center gap-2 ${isDragging ? 'bg-blue-50 border-blue-400' : ''}`}
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
      >
        Upload Image
      </button>
      <form onSubmit={handleSubmit} className="flex-1 flex items-center gap-2">
        <input
          type="text"
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          placeholder="Type a message..."
          className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
        />
        <button
          type="submit"
          className="px-4 py-2 bg-gray-700 text-white rounded-lg hover:bg-gray-800 transition-colors text-sm font-medium flex-shrink-0"
        >
          Send
        </button>
      </form>
    </div>
  );
}

