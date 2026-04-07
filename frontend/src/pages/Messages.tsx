import { useState, useEffect, useRef } from 'react';
import { useSearchParams } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { toast } from 'react-toastify';
import { api } from '@/services/api';
import { useAuth } from '@/contexts/AuthContext';
import { LoadingPage, Button } from '@/components/common';
import { MessageThread } from '@/components/message/MessageThread';
import { MessageBubble } from '@/components/message/MessageBubble';
import type { Message } from '@/types';

interface Thread {
  userId: number;
  userName: string;
  lastMessage: Message;
  unreadCount: number;
  messages: Message[];
}

interface SendMessageForm {
  content: string;
}

export function Messages() {
  const { user } = useAuth();
  const [searchParams] = useSearchParams();
  const [threads, setThreads] = useState<Thread[]>([]);
  const [activeThreadId, setActiveThreadId] = useState<number | null>(null);
  const [activeMessages, setActiveMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isSending, setIsSending] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<SendMessageForm>();

  useEffect(() => {
    loadThreads();

    // Check for URL parameters (booking or craftsman ID)
    const bookingId = searchParams.get('booking');
    const craftsmanId = searchParams.get('craftsman');

    // TODO: Handle opening specific conversation from URL params
  }, [searchParams]);

  useEffect(() => {
    if (activeThreadId) {
      loadMessages(activeThreadId);
    }
  }, [activeThreadId]);

  useEffect(() => {
    scrollToBottom();
  }, [activeMessages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const loadThreads = async () => {
    setIsLoading(true);
    try {
      const data = await api.getMessageThreads();
      setThreads(data);

      // Auto-select first thread if available
      if (data.length > 0 && !activeThreadId) {
        setActiveThreadId(data[0].userId);
      }
    } catch (error) {
      console.error('Failed to load message threads:', error);
      toast.error('Failed to load messages');
    } finally {
      setIsLoading(false);
    }
  };

  const loadMessages = async (otherUserId: number) => {
    try {
      // Find the thread to get booking ID if available
      const thread = threads.find(t => t.userId === otherUserId);
      const messages = thread?.messages || [];
      setActiveMessages(messages);

      // Mark messages as read
      const unreadMessages = messages.filter(
        (m) => !m.is_read && m.receiver_id === user?.id
      );
      for (const message of unreadMessages) {
        try {
          await api.markMessageAsRead(message.id);
        } catch (error) {
          console.error('Failed to mark message as read:', error);
        }
      }
    } catch (error) {
      console.error('Failed to load messages:', error);
      toast.error('Failed to load conversation');
    }
  };

  const onSubmit = async (data: SendMessageForm) => {
    if (!activeThreadId) return;

    setIsSending(true);
    try {
      const newMessage = await api.sendMessage(activeThreadId, data.content);
      setActiveMessages((prev) => [...prev, newMessage]);
      reset();

      // Update thread's last message
      setThreads((prev) =>
        prev.map((thread) =>
          thread.userId === activeThreadId
            ? { ...thread, lastMessage: newMessage }
            : thread
        )
      );
    } catch (error: any) {
      console.error('Failed to send message:', error);
      toast.error(error.response?.data?.detail || 'Failed to send message');
    } finally {
      setIsSending(false);
    }
  };

  if (isLoading) {
    return <LoadingPage />;
  }

  const activeThread = threads.find((t) => t.userId === activeThreadId);

  return (
    <div className="h-[calc(100vh-200px)]">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Messages</h1>
      </div>

      <div className="card p-0 h-full flex">
        {/* Thread List Sidebar */}
        <div className="w-80 border-r border-gray-200 flex flex-col">
          <div className="p-4 border-b border-gray-200">
            <h2 className="font-semibold">Conversations</h2>
          </div>

          <div className="flex-1 overflow-y-auto">
            {threads.length > 0 ? (
              threads.map((thread) => (
                <MessageThread
                  key={thread.userId}
                  otherUser={{ id: thread.userId, name: thread.userName }}
                  lastMessage={thread.lastMessage}
                  unreadCount={thread.unreadCount}
                  onClick={() => setActiveThreadId(thread.userId)}
                  isActive={thread.userId === activeThreadId}
                />
              ))
            ) : (
              <div className="p-8 text-center text-gray-500">
                <p>No messages yet</p>
                <p className="text-sm mt-2">
                  Start a conversation from a booking or craftsman profile
                </p>
              </div>
            )}
          </div>
        </div>

        {/* Conversation View */}
        <div className="flex-1 flex flex-col">
          {activeThread ? (
            <>
              {/* Conversation Header */}
              <div className="p-4 border-b border-gray-200">
                <h2 className="font-semibold text-lg">{activeThread.userName}</h2>
              </div>

              {/* Messages */}
              <div className="flex-1 overflow-y-auto p-4 bg-gray-50">
                {activeMessages.length > 0 ? (
                  activeMessages.map((message) => (
                    <MessageBubble
                      key={message.id}
                      message={message}
                      isOwn={message.sender_id === user?.id}
                    />
                  ))
                ) : (
                  <div className="flex items-center justify-center h-full text-gray-500">
                    No messages in this conversation yet
                  </div>
                )}
                <div ref={messagesEndRef} />
              </div>

              {/* Send Message Form */}
              <div className="p-4 border-t border-gray-200 bg-white">
                <form onSubmit={handleSubmit(onSubmit)} className="flex gap-2">
                  <input
                    type="text"
                    className={`input flex-1 ${errors.content ? 'border-red-500' : ''}`}
                    placeholder="Type your message..."
                    {...register('content', {
                      required: 'Message cannot be empty',
                      minLength: { value: 1, message: 'Message cannot be empty' },
                    })}
                  />
                  <Button type="submit" isLoading={isSending}>
                    Send
                  </Button>
                </form>
                {errors.content && (
                  <p className="text-red-500 text-sm mt-1">{errors.content.message}</p>
                )}
              </div>
            </>
          ) : (
            <div className="flex items-center justify-center h-full text-gray-500">
              Select a conversation to view messages
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
