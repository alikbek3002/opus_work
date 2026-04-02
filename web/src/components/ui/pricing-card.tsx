import React from 'react';
import { cn } from '@/lib/utils';

function Card({ className, ...props }: React.ComponentProps<'div'>) {
    return (
        <div
            className={cn(
                'bg-card relative w-full rounded-2xl dark:bg-transparent',
                'p-1.5 shadow-xl backdrop-blur-xl',
                'dark:border-border/80 border',
                className,
            )}
            {...props}
        />
    );
}

function Header({
    className,
    children,
    glassEffect = true,
    ...props
}: React.ComponentProps<'div'> & {
    glassEffect?: boolean;
}) {
    return (
        <div
            className={cn(
                'bg-muted/80 dark:bg-muted/50 relative mb-4 rounded-xl border p-6 flex flex-col',
                className,
            )}
            {...props}
        >
            {/* Top glass gradient */}
            {glassEffect && (
                <div
                    aria-hidden="true"
                    className="absolute inset-x-0 top-0 h-48 rounded-[inherit]"
                    style={{
                        background:
                            'linear-gradient(180deg, rgba(255,255,255,0.07) 0%, rgba(255,255,255,0.03) 40%, rgba(0,0,0,0) 100%)',
                    }}
                />
            )}
            <div className="relative z-10 w-full flex flex-col h-full rounded-[inherit]">{children}</div>
        </div>
    );
}

function Plan({ className, ...props }: React.ComponentProps<'div'>) {
    return (
        <div
            className={cn('mb-6 flex items-center justify-between', className)}
            {...props}
        />
    );
}

function Description({ className, ...props }: React.ComponentProps<'p'>) {
    return (
        <p className={cn('text-muted-foreground text-sm', className)} {...props} />
    );
}

function PlanName({ className, ...props }: React.ComponentProps<'div'>) {
    return (
        <div
            className={cn(
                "text-muted-foreground flex items-center gap-2 text-base font-semibold [&_svg:not([class*='size-'])]:size-5",
                className,
            )}
            {...props}
        />
    );
}

function Badge({ className, ...props }: React.ComponentProps<'span'>) {
    return (
        <span
            className={cn(
                'border-primary/20 text-primary bg-primary/10 rounded-full border px-3 py-1 text-xs font-semibold',
                className,
            )}
            {...props}
        />
    );
}

function Price({ className, ...props }: React.ComponentProps<'div'>) {
    return (
        <div className={cn('mb-3 flex items-end gap-1', className)} {...props} />
    );
}

function MainPrice({ className, ...props }: React.ComponentProps<'span'>) {
    return (
        <span
            className={cn('text-4xl font-extrabold tracking-tight', className)}
            {...props}
        />
    );
}

function Period({ className, ...props }: React.ComponentProps<'span'>) {
    return (
        <span
            className={cn('text-muted-foreground pb-1 text-base', className)}
            {...props}
        />
    );
}

function OriginalPrice({ className, ...props }: React.ComponentProps<'span'>) {
    return (
        <span
            className={cn(
                'text-muted-foreground mr-2 text-lg line-through font-normal',
                className,
            )}
            {...props}
        />
    );
}

function Body({ className, ...props }: React.ComponentProps<'div'>) {
    return <div className={cn('space-y-6 lg:p-4 p-2', className)} {...props} />;
}

function List({ className, ...props }: React.ComponentProps<'ul'>) {
    return <ul className={cn('space-y-4', className)} {...props} />;
}

function ListItem({ className, ...props }: React.ComponentProps<'li'>) {
    return (
        <li
            className={cn(
                'text-foreground flex items-start gap-3 text-sm font-medium',
                className,
            )}
            {...props}
        />
    );
}

function Separator({
    children,
    className,
    ...props
}: React.ComponentProps<'div'> & {
    children?: string;
    className?: string;
}) {
    return (
        <div
            className={cn(
                'text-muted-foreground flex items-center gap-3 text-sm my-6',
                className,
            )}
            {...props}
        >
            <span className="bg-border h-[1px] flex-1" />
            {children && <span className="text-muted-foreground shrink-0">{children}</span>}
            <span className="bg-border h-[1px] flex-1" />
        </div>
    );
}

export {
    Card,
    Header,
    Description,
    Plan,
    PlanName,
    Badge,
    Price,
    MainPrice,
    Period,
    OriginalPrice,
    Body,
    List,
    ListItem,
    Separator,
};
