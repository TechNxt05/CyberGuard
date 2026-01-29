import { cn } from "@/lib/utils"
import { ButtonHTMLAttributes, forwardRef } from "react"

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
    variant?: "primary" | "secondary" | "danger" | "ghost"
}

const Button = forwardRef<HTMLButtonElement, ButtonProps>(
    ({ className, variant = "primary", ...props }, ref) => {
        const variants = {
            primary: "bg-blue-600 text-white hover:bg-blue-700 shadow-[0_0_15px_rgba(37,99,235,0.5)]",
            secondary: "bg-white/10 text-white hover:bg-white/20 border border-white/10",
            danger: "bg-red-600 text-white hover:bg-red-700 shadow-[0_0_15px_rgba(220,38,38,0.5)]",
            ghost: "text-gray-400 hover:text-white hover:bg-white/5",
        }

        return (
            <button
                ref={ref}
                className={cn(
                    "inline-flex h-10 items-center justify-center rounded-lg px-6 text-sm font-medium transition-all active:scale-95 disabled:opacity-50",
                    variants[variant],
                    className
                )}
                {...props}
            />
        )
    }
)
Button.displayName = "Button"

export { Button }
