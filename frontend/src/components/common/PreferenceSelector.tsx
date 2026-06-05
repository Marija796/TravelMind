interface Option {
  value: string
  label: string
  icon?: React.ReactNode
}

interface PreferenceSelectorProps {
  label?: string
  options: Option[]
  selected: string[]
  onChange: (selected: string[]) => void
  maxSelect?: number
  singleSelect?: boolean
}

export default function PreferenceSelector({
  label,
  options,
  selected,
  onChange,
  maxSelect,
  singleSelect,
}: PreferenceSelectorProps) {
  const toggle = (value: string) => {
    if (singleSelect) {
      onChange(selected.includes(value) ? [] : [value])
      return
    }
    if (selected.includes(value)) {
      onChange(selected.filter((v) => v !== value))
    } else {
      if (maxSelect && selected.length >= maxSelect) return
      onChange([...selected, value])
    }
  }

  return (
    <div>
      {label && (
        <p className="text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">{label}</p>
      )}
      <div className="flex flex-wrap gap-2">
        {options.map((opt) => {
          const active = selected.includes(opt.value)
          return (
            <button
              key={opt.value}
              type="button"
              onClick={() => toggle(opt.value)}
              className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-sm font-medium border transition-all duration-200 ${
                active
                  ? 'bg-primary-600 border-primary-600 text-white shadow-sm shadow-primary-600/20'
                  : 'bg-white dark:bg-slate-800 border-slate-200 dark:border-slate-600 text-slate-700 dark:text-slate-300 hover:border-primary-400 dark:hover:border-primary-500'
              }`}
            >
              {opt.icon}
              {opt.label}
            </button>
          )
        })}
      </div>
    </div>
  )
}
