import { BadgeCheck, Clock3, ShieldX, type LucideIcon } from "lucide-react";

import { cn } from "@/lib/utils";
import { type VerificationStatus } from "@/lib/api";

interface VerificationBadgeProps {
    status?: VerificationStatus | null;
    isVerified?: boolean;
    className?: string;
}

const statusMeta: Record<VerificationStatus, { label: string; className: string; icon: LucideIcon }> = {
    verified: {
        label: "Верифицирован",
        className: "border-emerald-500/20 bg-emerald-500/10 text-emerald-700",
        icon: BadgeCheck,
    },
    pending: {
        label: "На проверке",
        className: "border-amber-500/20 bg-amber-500/10 text-amber-700",
        icon: Clock3,
    },
    rejected: {
        label: "Не верифицирован",
        className: "border-rose-500/20 bg-rose-500/10 text-rose-700",
        icon: ShieldX,
    },
};

export function normalizeVerificationStatus(
    status?: VerificationStatus | null,
    isVerified?: boolean
): VerificationStatus {
    if (status === "verified" || status === "pending" || status === "rejected") {
        return status;
    }
    return isVerified ? "verified" : "pending";
}

export function getVerificationLabel(
    status?: VerificationStatus | null,
    isVerified?: boolean
): string {
    return statusMeta[normalizeVerificationStatus(status, isVerified)].label;
}

export default function VerificationBadge({
    status,
    isVerified,
    className,
}: VerificationBadgeProps) {
    const normalizedStatus = normalizeVerificationStatus(status, isVerified);
    const meta = statusMeta[normalizedStatus];
    const Icon = meta.icon;

    return (
        <span
            className={cn(
                "inline-flex items-center gap-1.5 rounded-full border px-2.5 py-1 text-xs font-semibold",
                meta.className,
                className
            )}
        >
            <Icon className="h-3.5 w-3.5" />
            {meta.label}
        </span>
    );
}
