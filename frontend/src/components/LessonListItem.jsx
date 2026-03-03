import React from 'react'
import { Circle, CheckCircle2 } from 'lucide-react'
import { useIntersectionObserverContinuous } from '../hooks/useIntersectionObserver'

/**
 * LessonListItem component with lazy rendering
 * Only renders when visible in the module list to improve performance
 */
const LessonListItem = ({ 
  lesson, 
  isSelected, 
  isCompleted, 
  onSelect 
}) => {
  const [ref, isVisible] = useIntersectionObserverContinuous()

  // Don't render content if not visible, just reserve space
  if (!isVisible) {
    return (
      <div 
        ref={ref}
        className="h-16 border-b border-gray-200"
        style={{ minHeight: '64px' }}
      />
    )
  }

  return (
    <button
      ref={ref}
      onClick={() => onSelect(lesson)}
      className={`w-full px-4 py-3 flex items-start gap-3 hover:bg-gray-100 transition-colors text-left border-b border-gray-200 ${
        isSelected ? 'bg-primary-50 border-l-4 border-primary-600' : ''
      }`}
    >
      {isCompleted ? (
        <CheckCircle2 className="text-green-600 mt-0.5 flex-shrink-0" size={18} />
      ) : (
        <Circle className="text-gray-300 mt-0.5 flex-shrink-0" size={18} />
      )}
      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium text-gray-900 truncate">
          {lesson.title}
        </p>
        <p className="text-xs text-gray-500 mt-0.5">
          {lesson.duration_minutes} min
        </p>
      </div>
    </button>
  )
}

export default LessonListItem
