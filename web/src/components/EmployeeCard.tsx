import * as React from "react";
import { getPhotoUrl, type EmployeeCard as EmployeeCardType } from "@/lib/api";
import { UserSearch, Eye, BriefcaseBusiness, MapPin, BadgeCheck, Clock, UserRound } from "lucide-react";

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
                    <div className="flex items-start justify-between gap-3">
                        {employee.telegram_id ? (
                            <div className="relative h-12 w-12 sm:h-14 sm:w-14 overflow-hidden rounded-full border border-primary/10 bg-muted shrink-0 shadow-sm">
                                <img
                                    src={getPhotoUrl(employee.telegram_id)}
                                    alt={employee.full_name}
                                    className="h-full w-full object-cover"
                                    onError={(e) => {
                                        (e.currentTarget.parentElement as HTMLElement).innerHTML = `<div class="flex h-full w-full items-center justify-center text-muted-foreground"><svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="opacity-30"><circle cx="12" cy="8" r="5"/><path d="M20 21a8 8 0 0 0-16 0"/></svg></div>`
                                    }}
                                />
                            </div>
                        ) : (
                            <div className="flex h-12 w-12 sm:h-14 sm:w-14 items-center justify-center rounded-full border border-primary/10 bg-muted text-muted-foreground shrink-0 shadow-sm">
                                <UserRound className="h-6 w-6 sm:h-7 sm:w-7 opacity-30" />
                            </div>
                        )}
                        <div className="flex-1 min-w-0">
                            <h3 className="flex items-center gap-2 text-lg font-bold text-card-foreground">
                                <span className="truncate">{employee.full_name}</span>
                                {employee.is_verified && <BadgeCheck className="h-4 w-4 text-emerald-500 shrink-0" />}
                            </h3>
                            <p className="mt-1 flex items-center gap-1.5 text-sm font-medium text-primary/90 leading-tight">
                                <BriefcaseBusiness className="h-4 w-4 shrink-0" />
                                <span className="line-clamp-2">{employee.specializations || "Специализация уточняется"}</span>
                            </p>
                        </div>
                    </div>
                </div>

                <div className="grid grid-cols-2 gap-2 text-xs sm:text-sm text-muted-foreground mt-1">
                    <div className="flex items-center gap-1.5 rounded-md bg-muted/40 px-2 py-2">
                        <span className="font-semibold text-foreground">{employee.age || "-"} лет</span>
                        <span className="text-muted-foreground/50">•</span>
                        <span>{employee.gender === "Мужчина" ? "Муж." : employee.gender === "Женщина" ? "Жен." : "-"}</span>
                    </div>
                    <div className="flex items-center gap-1.5 rounded-md bg-muted/40 px-2 py-2 min-w-0">
                        <MapPin className="h-3.5 w-3.5 shrink-0" />
                        <span className="truncate">{employee.district || "Район не указан"}</span>
                    </div>
                    <div className="col-span-2 flex items-center gap-1.5 rounded-md bg-muted/40 px-2 py-2 min-w-0">
                        <Clock className="h-3.5 w-3.5 shrink-0" />
                        <span className="truncate">{employee.experience ? `Опыт: ${employee.experience}` : "Опыт работы не указан"}</span>
                    </div>
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
