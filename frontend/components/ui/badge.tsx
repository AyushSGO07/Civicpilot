import * as React from "react";
import { cn } from "@/lib/utils";

export interface BadgeProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: "default" | "secondary" | "outline" | "cyan" | "success" | "warning";
}

function Badge({
  className,
  variant = "default",
  ...props
}: BadgeProps) {
  const variantStyles = {
    default:
      "bg-civic-blue text-white hover:bg-civic-blue-hover",
    secondary:
      "bg-slate-100 text-slate-800 hover:bg-slate-200",
    outline:
      "border border-slate-200 text-slate-700",
    cyan:
      "bg-civic-cyan/15 text-[#008ba3] border border-civic-cyan/30",
    success:
      "bg-emerald-50 text-emerald-700 border border-emerald-200",
    warning:
      "bg-amber-50 text-amber-800 border border-amber-200",
  };

  return (
    <div
      className={cn(
        "inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2",
        variantStyles[variant],
        className
      )}
      {...props}
    />
  );
}

export { Badge };
