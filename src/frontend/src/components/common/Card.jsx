export default function Card({ children, className = '', hover = false, onClick }) {
  return (
    <div
      className={`bg-white shadow-sm ring-1 ring-black/[0.03] border border-slate-100 rounded-xl transition-all duration-200 ${
        hover ? 'hover:-translate-y-0.5 hover:shadow-md hover:border-slate-200 cursor-pointer' : ''
      } ${className}`}
      onClick={onClick}
    >
      {children}
    </div>
  )
}

export function CardHeader({ children, className = '' }) {
  return <div className={`px-5 py-4 border-b border-slate-100 ${className}`}>{children}</div>
}

export function CardBody({ children, className = '' }) {
  return <div className={`px-5 py-4 ${className}`}>{children}</div>
}
