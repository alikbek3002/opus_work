import * as React from "react";
import { type EmployeeCard as EmployeeCardType } from "@/lib/api";
import { ProfileCard } from "@/components/ui/profile-card";
import { UserSearch, Eye } from "lucide-react";

interface EmployeeCardProps {
    employee: EmployeeCardType;
    onOpen: (employee: EmployeeCardType) => void;
    isViewed?: boolean;
    className?: string;
}

const DEFAULT_AVATAR = "https://images.unsplash.com/photo-1497366754035-f200968a6e72?auto=format&fit=crop&w=150&q=80";

export const EmployeeCard = React.forwardRef<HTMLDivElement, EmployeeCardProps>(
    ({ employee, onOpen, isViewed, className }, ref) => {
        const stats = [
            { label: "Возраст", value: employee.age || "-" },
            { label: "Пол", value: employee.gender === "Мужчина" ? "Муж" : employee.gender === "Женщина" ? "Жен" : "-" },
            { label: "Район", value: employee.district || "Не указан" },
        ];

        const actions = [
            {
                label: isViewed ? "Открыть анкету" : "Подробности",
                variant: (isViewed ? "secondary" : "default") as any,
                onClick: () => onOpen(employee),
                className: "font-semibold w-full",
                children: (
                    <>
                        {isViewed ? <Eye className="w-4 h-4 mr-2" /> : <UserSearch className="w-4 h-4 mr-2" />}
                        {isViewed ? "Анкета и контакты" : "Подробности"}
                    </>
                )
            }
        ];

        return (
            <div ref={ref}>
                <ProfileCard
                    avatarSrc={DEFAULT_AVATAR}
                    name={employee.full_name}
                    handle={employee.specializations || "Специализация уточняется"}
                    bio={employee.experience || "Опыт работы не указан."}
                    stats={stats}
                    actions={actions as any}
                    onClick={() => onOpen(employee)}
                    isUnlocked={isViewed}
                    className={className}
                />
            </div>
        );
    }
);

EmployeeCard.displayName = "EmployeeCard";
export default EmployeeCard;
