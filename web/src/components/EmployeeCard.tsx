import * as React from "react";
import { getPhotoUrl, type EmployeeCard as EmployeeCardType } from "@/lib/api";
import { UserSearch, Eye, MapPin, BadgeCheck, Clock } from "lucide-react";
import EmployeeActivityBadge from "@/components/EmployeeActivityBadge";

interface EmployeeCardProps {
    employee: EmployeeCardType;
    onOpen: (employee: EmployeeCardType) => void;
    isViewed?: boolean;
    className?: string;
}

export const EmployeeCard = React.forwardRef<HTMLDivElement, EmployeeCardProps>(
    ({ employee, onOpen, isViewed, className }, ref) => {
        return (
            <div
                ref={ref}
                onClick={() => onOpen(employee)}
                className={`group cursor-pointer rounded-xl border border-border/60 bg-card p-5 transition-all hover:border-primary/40 hover:shadow-md flex flex-col gap-4 ${className || ""}`}
            >
                <div>
                    <div className="flex items-start gap-4">
                        {employee.telegram_id ? (
                            <div className="relative h-14 w-14 overflow-hidden rounded-full border border-primary/10 bg-muted shrink-0 shadow-sm">
                                <img
                                    src={getPhotoUrl(employee.telegram_id)}
                                    alt={employee.full_name}
                                    className="h-full w-full object-cover"
                                    onError={(e) => {
                                        (e.currentTarget.parentElement as HTMLElement).innerHTML = `<div class="flex h-full w-full items-center justify-center overflow-hidden bg-white p-2"><img src="/logo.png" alt="Opus" class="h-full w-full object-contain" /></div>`
                                    }}
                                />
                            </div>
                        ) : (
                            <div className="flex h-14 w-14 items-center justify-center rounded-full border border-primary/10 bg-muted text-muted-foreground shrink-0 shadow-sm overflow-hidden p-2 bg-white">
                                <img src="/logo.png" alt="Opus" className="h-full w-full object-contain" />
                            </div>
                        )}
                        <div className="flex-1 min-w-0 pt-0.5">
                            <h3 className="flex items-center gap-1.5 text-lg font-bold text-card-foreground leading-tight">
                                <span className="line-clamp-2">
                                    {employee.full_name} — {employee.age || "?"} лет — {employee.specializations || "Специализация уточняется"}
                                </span>
                                {employee.is_verified && <BadgeCheck className="h-5 w-5 text-emerald-500 shrink-0" />}
                            </h3>

                            <EmployeeActivityBadge
                                employmentType={employee.employment_type}
                                activitySignal={employee.activity_signal}
                                activitySignalUpdatedAt={employee.activity_signal_updated_at}
                                compact
                                className="mt-2"
                            />
                        </div>
                    </div>
                </div>

                <div className="flex flex-wrap gap-x-4 gap-y-2 text-sm text-card-foreground/80 mt-1">
                    <div className="flex items-center gap-1.5 min-w-0">
                        <MapPin className="h-4 w-4 shrink-0 text-muted-foreground" />
                        <span className="truncate">{employee.district || "Район не указан"}</span>
                    </div>
                    <div className="flex items-center gap-1.5 min-w-0">
                        <Clock className="h-4 w-4 shrink-0 text-muted-foreground" />
                        <span className="truncate">{employee.experience ? `Опыт: ${employee.experience}` : "Опыт работы не указан"}</span>
                    </div>
                    {employee.gender && (
                        <div className="flex items-center gap-1.5 min-w-0">
                            <span className="text-muted-foreground">•</span>
                            <span>{employee.gender === "Мужчина" ? "Муж." : employee.gender === "Женщина" ? "Жен." : ""}</span>
                        </div>
                    )}
                </div>

                <button
                    className={`mt-2 flex w-full items-center justify-center gap-2 rounded-lg py-2.5 text-sm font-semibold transition-colors ${isViewed
                        ? "bg-secondary text-secondary-foreground hover:bg-secondary/80"
                        : "bg-primary text-primary-foreground hover:bg-primary/90"
                        }`}
                >
                    {isViewed ? <Eye className="w-4 h-4" /> : <UserSearch className="w-4 h-4" />}
                    {isViewed ? "Анкета и контакты" : "Подробности"}
                </button>
            </div>
        );
    }
);

EmployeeCard.displayName = "EmployeeCard";
export default EmployeeCard;
