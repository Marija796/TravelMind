interface ActivityChipProps {
  label: string
  selected?: boolean
  onClick?: () => void
}

export default function ActivityChip({ label, selected, onClick }: ActivityChipProps) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-medium transition-all duration-200 ${
        selected
          ? 'bg-primary-600 text-white'
          : 'bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-600'
      } ${onClick ? 'cursor-pointer' : 'cursor-default'}`}
    >
      {label}
    </button>
  )
}
