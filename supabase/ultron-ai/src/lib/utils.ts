import { clsx, type ClassValue } from 'clsx'
import { twMerge } from 'tailwind-merge'

/**
 * Merge Tailwind CSS class names, resolving conflicts.
 */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

/**
 * Format an ISO timestamp string (or Date) into a human-readable time.
 * Returns e.g. "14:32" for same-day timestamps, or "Mar 8 14:32" for older ones.
 */
export function formatTime(timestamp: string | Date): string {
  const date = typeof timestamp === 'string' ? new Date(timestamp) : timestamp
  if (isNaN(date.getTime())) return 'Invalid date'

  const now = new Date()
  const isToday =
    date.getFullYear() === now.getFullYear() &&
    date.getMonth() === now.getMonth() &&
    date.getDate() === now.getDate()

  const timeStr = date.toLocaleTimeString([], {
    hour: '2-digit',
    minute: '2-digit',
  })

  if (isToday) {
    return timeStr
  }

  const dateStr = date.toLocaleDateString([], { month: 'short', day: 'numeric' })
  return `${dateStr} ${timeStr}`
}

/**
 * Format a byte count into a human-readable file size string.
 * e.g. formatFileSize(1536) → "1.5 KB"
 */
export function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 B'
  const units = ['B', 'KB', 'MB', 'GB', 'TB']
  const k = 1024
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  const value = bytes / Math.pow(k, i)
  return `${value % 1 === 0 ? value : value.toFixed(1)} ${units[i]}`
}

/**
 * Truncate a string to a maximum length, appending "…" if needed.
 */
export function truncate(str: string, maxLength: number): string {
  return str.length <= maxLength ? str : str.slice(0, maxLength - 1) + '…'
}
