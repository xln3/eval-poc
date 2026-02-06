const variants = {
  primary: 'bg-blue-600 hover:bg-blue-700 text-white shadow-sm',
  secondary: 'bg-slate-100 hover:bg-slate-200 text-slate-700',
  danger: 'bg-red-50 hover:bg-red-100 text-red-600 border border-red-200',
  ghost: 'hover:bg-slate-100 text-slate-500 hover:text-slate-700',
}

const sizes = {
  sm: 'px-3 py-1.5 text-xs',
  md: 'px-5 py-2.5 text-sm',
  lg: 'px-6 py-3 text-base',
}

export default function Button({ children, variant = 'primary', size = 'md', disabled, className = '', ...props }) {
  return (
    <button
      className={`${variants[variant]} ${sizes[size]} rounded-lg font-medium transition-all duration-150 disabled:opacity-50 disabled:cursor-not-allowed inline-flex items-center justify-center gap-2 focus-visible:ring-2 focus-visible:ring-blue-500/50 focus-visible:ring-offset-2 focus-visible:outline-none ${className}`}
      disabled={disabled}
      {...props}
    >
      {children}
    </button>
  )
}
