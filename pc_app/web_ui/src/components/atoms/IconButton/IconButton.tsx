import type { ButtonHTMLAttributes, ReactNode } from "react";

interface IconButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  label: string;
  icon: ReactNode;
}

export function IconButton({ label, icon, ...props }: IconButtonProps) {
  return (
    <button className="icon-button" title={label} aria-label={label} {...props}>
      {icon}
    </button>
  );
}
