import { cn } from "@/lib/utils"

export function Card({ className, children, ...props }: React.HTMLAttributes<HTMLDivElement>) {
    return (
        <div
            className={cn(
                "rounded-xl border border-white/10 bg-white/5 p-6 shadow-xl backdrop-blur-md transition-all hover:bg-white/10",
                className
            )}
            {...props}
        >
            {children}
        </div>
    )
}
