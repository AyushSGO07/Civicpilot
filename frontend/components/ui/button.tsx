import * as React from "react";
import { cn } from "@/lib/utils";

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "default" | "outline" | "ghost" | "cyan" | "secondary" | "link";
  size?: "default" | "sm" | "lg" | "icon";
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = "default", size = "default", children, ...props }, ref) => {
    const baseStyles =
      "inline-flex items-center justify-center whitespace-nowrap rounded-lg text-sm font-semibold ring-offset-background transition-all duration-150 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-civic-blue focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 cursor-pointer select-none active:scale-[0.98]";

    const variantStyles = {
      default:
        "bg-civic-blue text-white shadow hover:bg-civic-blue-hover hover:shadow-md",
      outline:
        "border border-slate-300 bg-white text-navy hover:bg-canvas hover:border-slate-400 shadow-xs",
      ghost:
        "text-navy hover:bg-slate-100/80 hover:text-civic-blue",
      cyan:
        "bg-civic-cyan text-white shadow hover:bg-civic-cyan-dark hover:shadow-md",
      secondary:
        "bg-slate-100 text-navy hover:bg-slate-200",
      link:
        "text-civic-blue underline-offset-4 hover:underline p-0 h-auto font-normal",
    };

    const sizeStyles = {
      default: "h-10 px-4 py-2",
      sm: "h-8 rounded-md px-3 text-xs",
      lg: "h-12 rounded-xl px-6 text-base font-semibold",
      icon: "h-10 w-10 p-0",
    };

    return (
      <button
        ref={ref}
        className={cn(baseStyles, variantStyles[variant], sizeStyles[size], className)}
        {...props}
      >
        {children}
      </button>
    );
  }
);

Button.displayName = "Button";

export { Button };
