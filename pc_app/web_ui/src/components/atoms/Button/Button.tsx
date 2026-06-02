import type { ButtonHTMLAttributes, ReactNode } from "react";

type ButtonVariant = "primary" | "secondary" | "danger";

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  children: ReactNode;
  variant?: ButtonVariant;
  isActive?: boolean;
}

export function Button({ 
  children, 
  variant = "secondary", 
  isActive = false,
  className = "",
  ...props 
}: ButtonProps) {
  const activeClass = isActive ? "button-active" : "";
  return (
    <button className={`button button-${variant} ${activeClass} ${className}`} {...props}>
      {children}
    </button>
  );
}
