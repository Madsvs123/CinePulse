import { useState, type ReactNode } from 'react'

export function Panel({ children, className = '' }: { children: ReactNode; className?: string }) {
  return <section className={`cp-panel ${className}`}>{children}</section>
}

export function Button({
  children,
  onClick,
  kind = 'solid',
  type = 'button',
}: {
  children: ReactNode
  onClick?: () => void
  kind?: 'solid' | 'ghost' | 'gold'
  type?: 'button' | 'submit'
}) {
  return (
    <button type={type} className={`cp-btn ${kind === 'solid' ? '' : kind}`} onClick={onClick}>
      {children}
    </button>
  )
}

export function Chip({ label, active, onClick }: { label: string; active?: boolean; onClick?: () => void }) {
  return (
    <button type="button" className={`cp-chip ${active ? 'active' : ''}`} onClick={onClick}>
      {label}
    </button>
  )
}

export function Field({ label, children }: { label: string; children: ReactNode }) {
  return (
    <label className="cp-form">
      <span className="cp-muted">{label}</span>
      {children}
    </label>
  )
}

export function Empty({ title, copy }: { title: string; copy: string }) {
  return (
    <Panel>
      <h3 className="cp-display">{title}</h3>
      <p className="cp-muted">{copy}</p>
    </Panel>
  )
}

export function Spoiler({ text, flagged }: { text: string; flagged: boolean }) {
  const [open, setOpen] = useState(false)
  if (!flagged) return <p>{text}</p>
  return (
    <div>
      <p className={`cp-spoiler ${open ? 'revealed' : ''}`}>{text}</p>
      <Button kind="ghost" onClick={() => setOpen((value) => !value)}>
        {open ? 'Hide spoilers' : 'Reveal spoilers'}
      </Button>
    </div>
  )
}
