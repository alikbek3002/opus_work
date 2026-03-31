import * as React from "react";
import { motion, useReducedMotion } from "framer-motion";
import { cn } from "@/lib/utils";
import { Button, ButtonProps } from "@/components/ui/button";

interface Stat {
    label: string;
    value: string | number;
}

interface Action extends ButtonProps {
    label: string;
    onClick: (e: React.MouseEvent) => void;
}

export interface ProfileCardProps {
    avatarSrc: string;
    name: string;
    handle: string;
    bio: string;
    stats: Stat[];
    actions: Action[];
    className?: string;
    onClick?: () => void;
    isUnlocked?: boolean;
}

export const ProfileCard = React.forwardRef<HTMLDivElement, ProfileCardProps>(
    ({ avatarSrc, name, handle, bio, stats, actions, className, onClick, isUnlocked }, ref) => {
        const shouldReduceMotion = useReducedMotion();
        const shouldAnimate = !shouldReduceMotion;

        const cardVariants = {
            hidden: { opacity: 0, y: 20 },
            visible: {
                opacity: 1,
                y: 0,
                transition: {
                    duration: 0.4,
                    ease: "easeOut" as any,
                    staggerChildren: 0.1,
                },
            },
            hover: shouldAnimate ? {
                y: -4,
                boxShadow: "0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1)"
            } : {}
        };

        const itemVariants = {
            hidden: { opacity: 0, y: 10 },
            visible: { opacity: 1, y: 0 },
        };

        return (
            <motion.div
                ref={ref}
                className={cn(
                    "w-full rounded-2xl border bg-card text-card-foreground shadow-sm p-5 sm:p-6 flex flex-col gap-5 sm:gap-6 cursor-pointer relative overflow-hidden",
                    className
                )}
                variants={cardVariants}
                initial="hidden"
                animate="visible"
                whileHover="hover"
                onClick={onClick}
            >
                {isUnlocked && (
                    <div className="absolute top-0 right-0 bg-primary/10 text-primary px-3 py-1 rounded-bl-2xl text-xs font-semibold">
                        Контакт Открыт
                    </div>
                )}
                {/* Header Section */}
                <motion.div variants={itemVariants} className="flex items-center gap-4 mt-2">
                    <img
                        src={avatarSrc}
                        alt={name}
                        className="w-16 h-16 rounded-full object-cover border-2 border-border"
                    />
                    <div className="flex flex-col">
                        <h2 className="text-xl font-bold">{name}</h2>
                        <p className="text-sm font-medium text-primary/80">{handle}</p>
                    </div>
                </motion.div>

                {/* Bio Section */}
                <motion.p variants={itemVariants} className="text-sm text-muted-foreground line-clamp-3">
                    {bio}
                </motion.p>

                {/* Stats Section */}
                <motion.div
                    variants={itemVariants}
                    className="flex items-center justify-between text-center border-t border-b py-4"
                >
                    {stats.map((stat) => (
                        <div key={stat.label} className="flex flex-col items-center">
                            <span className="text-lg font-bold">{stat.value}</span>
                            <span className="text-xs text-muted-foreground tracking-wider uppercase mt-1">
                                {stat.label}
                            </span>
                        </div>
                    ))}
                </motion.div>

                {/* Actions Section */}
                <motion.div variants={itemVariants} className="flex items-center gap-3">
                    {actions.map(({ label, onClick: onActionClick, ...props }, index) => (
                        <Button
                            key={index}
                            {...props}
                            className={cn("flex-1", props.className)}
                            onClick={(e) => {
                                e.stopPropagation();
                                onActionClick(e);
                            }}
                        >
                            {label}
                        </Button>
                    ))}
                </motion.div>
            </motion.div>
        );
    }
);

ProfileCard.displayName = "ProfileCard";
