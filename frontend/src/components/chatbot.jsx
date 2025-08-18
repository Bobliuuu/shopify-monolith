import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, User } from 'lucide-react';

function ChatBot() {
  const [messages, setMessages] = useState([
    {
      id: 1,
      text: "Hello! I'm your AI assistant for store analytics. I can help you analyze your store data, generate reports, and provide insights about your business performance. What would you like to know?",
      sender: 'ai',
      timestamp: new Date(Date.now() - 1000 * 60 * 5).toLocaleTimeString()
    }
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  // Mock AI responses for demo purposes
  const mockAIResponses = [
    "Based on your store data, I can see that your conversion rate has improved by 15% this quarter. Would you like me to break down the key factors contributing to this growth?",
    "I've analyzed your product performance data. Your top-selling category is showing strong momentum with a 23% increase in sales volume compared to last month.",
    "Your customer acquisition cost has decreased by 8% while customer lifetime value has increased by 12%. This indicates improved targeting and retention strategies.",
    "I notice some interesting patterns in your checkout abandonment data. The main drop-off point is at the shipping options stage. Would you like recommendations to optimize this?",
    "Your inventory turnover rate is healthy at 6.2x annually. However, I've identified 3 products that might benefit from promotional pricing to clear slow-moving stock."
  ];

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    // Only scroll to bottom if there are more than 1 message (i.e., not on initial load)
    if (messages.length > 1) {
      scrollToBottom();
    }
  }, [messages]);

  const handleSendMessage = async () => {
    if (!inputValue.trim()) return;

    const userMessage = {
      id: messages.length + 1,
      text: inputValue,
      sender: 'user',
      timestamp: new Date().toLocaleTimeString()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    // Simulate AI response delay
    setTimeout(() => {
      const aiResponse = {
        id: messages.length + 2,
        text: mockAIResponses[Math.floor(Math.random() * mockAIResponses.length)],
        sender: 'ai',
        timestamp: new Date().toLocaleTimeString()
      };
      setMessages(prev => [...prev, aiResponse]);
      setIsLoading(false);
    }, 1500);
  };

  const handleKeyPress = (event) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      handleSendMessage();
    }
  };

  const setQuickPrompt = (prompt) => {
    setInputValue(prompt);
  };

  const MessageBubble = ({ message }) => (
    <div className={`flex gap-3 ${message.sender === 'user' ? 'flex-row-reverse' : ''}`}>
      <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center text-white text-sm font-medium ${
        message.sender === 'ai' ? 'bg-green-500' : 'bg-blue-500'
      }`}>
        {message.sender === 'ai' ? <Bot size={16} /> : <User size={16} />}
      </div>
      <div className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
        message.sender === 'user' 
          ? 'bg-blue-500 text-white' 
          : 'bg-gray-100 text-gray-900'
      }`}>
        <p className="text-sm">{message.text}</p>
        <p className={`text-xs mt-1 ${
          message.sender === 'user' ? 'text-blue-100' : 'text-gray-500'
        }`}>
          {message.timestamp}
        </p>
      </div>
    </div>
  );

  return (
    <div className="lg:col-span-3">
      <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
        {/* Chat Header */}
        <div className="px-6 py-4 border-b border-gray-200">
          <div className="flex items-center justify-between">
            <h2 className="font-semibold text-gray-900">Chat with AI Assistant</h2>
            <span className="px-2 py-1 bg-green-100 text-green-800 text-xs font-medium rounded-full">
              Online
            </span>
          </div>
        </div>

        {/* Messages Container */}
        <div className="h-96 overflow-y-auto p-6 space-y-4 bg-gray-50">
          {messages.map((message) => (
            <MessageBubble key={message.id} message={message} />
          ))}
          
          {isLoading && (
            <div className="flex gap-3">
              <div className="flex-shrink-0 w-8 h-8 rounded-full bg-green-500 flex items-center justify-center text-white">
                <Bot size={16} />
              </div>
              <div className="bg-gray-100 px-4 py-2 rounded-lg">
                <div className="flex items-center gap-2">
                  <div className="flex gap-1">
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                  </div>
                  <span className="text-sm text-gray-500">AI is thinking...</span>
                </div>
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <div className="p-6 border-t border-gray-200">
          <div className="flex gap-4">
            <textarea
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask me about your store performance, analytics, or any insights..."
              className="flex-1 border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent resize-none"
              rows={2}
            />
            <button
              onClick={handleSendMessage}
              disabled={!inputValue.trim() || isLoading}
              className="px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 disabled:bg-gray-300 disabled:cursor-not-allowed flex items-center gap-2"
            >
              <Send size={18} />
              Send
            </button>
          </div>

          {/* Quick Actions */}
          <div className="mt-4">
            <p className="text-sm text-gray-600 text-center mb-3">Try asking:</p>
            <div className="flex flex-wrap gap-2">
              <button 
                onClick={() => setQuickPrompt("What's my conversion rate this month?")}
                className="px-3 py-1 bg-gray-100 text-gray-700 rounded-full text-sm hover:bg-gray-200"
              >
                Conversion Rate
              </button>
              <button 
                onClick={() => setQuickPrompt("Show me top performing products")}
                className="px-3 py-1 bg-gray-100 text-gray-700 rounded-full text-sm hover:bg-gray-200"
              >
                Top Products
              </button>
              <button 
                onClick={() => setQuickPrompt("Generate a quarterly sales report")}
                className="px-3 py-1 bg-gray-100 text-gray-700 rounded-full text-sm hover:bg-gray-200"
              >
                Quarterly Report
              </button>
              <button 
                onClick={() => setQuickPrompt("Analyze customer retention")}
                className="px-3 py-1 bg-gray-100 text-gray-700 rounded-full text-sm hover:bg-gray-200"
              >
                Customer Retention
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default ChatBot;
