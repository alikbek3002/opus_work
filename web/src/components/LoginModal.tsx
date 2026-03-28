import { useState, useId } from "react";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Checkbox } from "@/components/ui/checkbox";
import { useAuth } from "@/hooks/useAuth";

interface LoginModalProps {
    isOpen: boolean;
    onClose: () => void;
}

export default function LoginModal({ isOpen, onClose }: LoginModalProps) {
    const id = useId();
    const { login, register, loading, error } = useAuth();
    const [isLoginView, setIsLoginView] = useState(true);

    // Форма обрабатывается неконтролируемо через FormData для лучшей производительности
    const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
        e.preventDefault();
        const formData = new FormData(e.currentTarget);
        const email = formData.get("email") as string;
        const password = formData.get("password") as string;

        try {
            if (isLoginView) {
                await login({ email, password });
            } else {
                const fullName = formData.get("fullName") as string;
                await register({ full_name: fullName, email, password });
            }
            onClose();
        } catch {
            // Ошибка обрабатывается и показывается из hook-а
        }
    };

    return (
        <Dialog open={isOpen} onOpenChange={(open) => !open && onClose()}>
            <DialogContent className="sm:max-w-md">
                <div className="flex flex-col items-center gap-2">
                    <div
                        className="flex h-11 w-11 shrink-0 items-center justify-center rounded-full border bg-primary/10 text-primary"
                        aria-hidden="true"
                    >
                        ◆
                    </div>
                    <DialogHeader>
                        <DialogTitle className="sm:text-center text-xl">
                            {isLoginView ? "С возвращением!" : "Создание аккаунта"}
                        </DialogTitle>
                        <DialogDescription className="sm:text-center">
                            {isLoginView
                                ? "Введите свои данные для входа в платформу"
                                : "Зарегистрируйтесь, чтобы просматривать карточки кандидатов"}
                        </DialogDescription>
                    </DialogHeader>
                </div>

                {error && <div className="text-sm font-medium text-destructive text-center mb-2">{error}</div>}

                <form onSubmit={handleSubmit} className="space-y-4">
                    {!isLoginView && (
                        <div className="space-y-2">
                            <Label htmlFor={`${id}-fullname`}>ФИО</Label>
                            <Input
                                id={`${id}-fullname`}
                                name="fullName"
                                type="text"
                                placeholder="Иван Иванов"
                                required={!isLoginView}
                            />
                        </div>
                    )}
                    <div className="space-y-2">
                        <Label htmlFor={`${id}-email`}>Email адрес</Label>
                        <Input
                            id={`${id}-email`}
                            name="email"
                            placeholder="name@company.com"
                            type="email"
                            autoComplete="username"
                            required
                        />
                    </div>
                    <div className="space-y-2">
                        <Label htmlFor={`${id}-password`}>Пароль</Label>
                        <Input
                            id={`${id}-password`}
                            name="password"
                            placeholder="••••••••"
                            type="password"
                            autoComplete={isLoginView ? "current-password" : "new-password"}
                            required
                        />
                    </div>

                    {isLoginView && (
                        <div className="flex items-center justify-between gap-2">
                            <div className="flex items-center gap-2">
                                <Checkbox id={`${id}-remember`} />
                                <Label
                                    htmlFor={`${id}-remember`}
                                    className="font-normal text-muted-foreground cursor-pointer"
                                >
                                    Запомнить меня
                                </Label>
                            </div>
                            <a className="text-sm font-medium text-primary hover:underline" href="#">
                                Забыли пароль?
                            </a>
                        </div>
                    )}

                    <Button type="submit" className="w-full" disabled={loading}>
                        {loading ? "Загрузка..." : isLoginView ? "Войти" : "Зарегистрироваться"}
                    </Button>
                </form>

                <div className="flex items-center gap-3 before:h-px before:flex-1 before:bg-border after:h-px after:flex-1 after:bg-border my-2">
                    <span className="text-xs text-muted-foreground">Или</span>
                </div>

                <Button
                    variant="outline"
                    type="button"
                    onClick={() => setIsLoginView(!isLoginView)}
                >
                    {isLoginView ? "Создать новый аккаунт" : "Уже есть аккаунт? Войти"}
                </Button>
            </DialogContent>
        </Dialog>
    );
}
