import { Search, X, SlidersHorizontal } from 'lucide-react'

interface SearchBarProps {
  value: string
  onChange: (v: string) => void
  placeholder?: string
  showFilterButton?: boolean
  onFilterToggle?: () => void
  isFilterOpen?: boolean
}

export default function SearchBar({ value, onChange, placeholder = 'Search destinations...', showFilterButton, onFilterToggle, isFilterOpen }: SearchBarProps) {
  return (
    <div className="flex gap-2">
      <div className="relative flex-1">
        <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400 pointer-events-none" />
        <input
          type="text"
          value={value}
          onChange={(e) => onChange(e.target.value)}
          placeholder={placeholder}
          className="input-base pl-10 pr-10 h-11"
        />
        {value && (
          <button
            onClick={() => onChange('')}
            className="absolute right-3 top-1/2 -translate-y-1/2 p-0.5 rounded hover:bg-slate-100 dark:hover:bg-slate-700 text-slate-400"
          >
            <X className="w-3.5 h-3.5" />
          </button>
        )}
      </div>
      {showFilterButton && (
        <button
          onClick={onFilterToggle}
          className={`flex items-center gap-2 px-4 h-11 rounded-xl border font-medium text-sm transition-all ${
            isFilterOpen
              ? 'bg-primary-600 border-primary-600 text-white'
              : 'bg-white dark:bg-slate-800 border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-300 hover:border-primary-400'
          }`}
        >
          <SlidersHorizontal className="w-4 h-4" />
          <span className="hidden sm:inline">Filters</span>
        </button>
      )}
    </div>
  )
}
