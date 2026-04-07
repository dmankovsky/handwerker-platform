import { formatDistanceToNow } from 'date-fns';
import type { Message } from '@/types';

interface MessageThreadProps {
  otherUser: {
    id: number;
    name: string;
  };
  lastMessage: Message;
  unreadCount: number;
  onClick: () => void;
  isActive?: boolean;
}

export function MessageThread({
  otherUser,
  lastMessage,
  unreadCount,
  onClick,
  isActive = false,
}: MessageThreadProps) {
  return (
    <button
      onClick={onClick}
      className={`w-full text-left p-4 border-b border-gray-200 hover:bg-gray-50 transition-colors ${
        isActive ? 'bg-primary-50 border-l-4 border-l-primary-600' : ''
      }`}
    >
      <div className="flex items-start justify-between mb-1">
        <div className="font-semibold text-gray-900">{otherUser.name}</div>
        <div className="text-xs text-gray-500">
          {formatDistanceToNow(new Date(lastMessage.created_at), { addSuffix: true })}
        </div>
      </div>

      <div className="flex items-center justify-between">
        <p className={`text-sm line-clamp-1 ${lastMessage.is_read ? 'text-gray-600' : 'text-gray-900 font-medium'}`}>
          {lastMessage.content}
        </p>
        {unreadCount > 0 && (
          <span className="ml-2 px-2 py-1 bg-primary-600 text-white text-xs rounded-full">
            {unreadCount}
          </span>
        )}
      </div>
    </button>
  );
}
