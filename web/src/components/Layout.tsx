import { useState, useEffect } from 'react';
import { Outlet, Link, useLocation, useNavigate } from 'react-router-dom';
import { BadgePercent, Megaphone, Users, CreditCard, LogOut, LogIn, Menu, X, Settings, User } from 'lucide-react';
import { useAuth } from '../hooks/useAuth';
import { useSubscription } from '../hooks/useTariffs';
import LoginModal from './LoginModal';
import SettingsModal from './SettingsModal';
import { InfiniteSlider } from './ui/infinite-slider';

const tariffAnnouncements = [
    'РАННИЙ ДОСТУП: СКИДКА ДЛЯ ПЕРВЫХ 50 ЗАКАЗЧИКОВ',
    'Пробный: 3 контакта',
    'Неделя: 25 контактов, до 8 в день — скидка 34%',
    'Месяц: 65 контактов, до 15 в день — скидка 45%',
    'Квартальный: 180 контактов, до 22 в день — скидка 40%',
    'Оплата проходит через Finik, ссылка формируется автоматически',
    'Скидка раннего доступа сохраняется при продлении',
    'Нажмите на ленту, чтобы перейти к оплате тарифов',
];

export default function Layout() {
    const location = useLocation();
    const navigate = useNavigate();
    const { isAuthenticated, userEmail, logout } = useAuth();
    const { data: subscription } = useSubscription();

    const [isLoginModalOpen, setIsLoginModalOpen] = useState(false);
    const [isSettingsModalOpen, setIsSettingsModalOpen] = useState(false);
    const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

    useEffect(() => {
        const handleOpenLogin = () => setIsLoginModalOpen(true);
        window.addEventListener('openLoginModal', handleOpenLogin);
        return () => window.removeEventListener('openLoginModal', handleOpenLogin);
    }, []);

    useEffect(() => {
        setIsMobileMenuOpen(false);
    }, [location.pathname]);

    return (
        <div className="min-h-screen bg-background text-foreground flex flex-col">
            <header className="sticky top-0 z-40 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
                <div
                    className="cursor-pointer border-b border-primary/20 bg-gradient-to-r from-white via-primary/5 to-white"
                    onClick={() => navigate('/tariffs')}
                    onKeyDown={(event) => {
                        if (event.key === 'Enter' || event.key === ' ') {
                            event.preventDefault();
                            navigate('/tariffs');
                        }
                    }}
                    role="button"
                    tabIndex={0}
                    aria-label="Перейти к тарифным планам"
                >
                    <div className="mx-auto flex h-14 max-w-7xl items-center gap-2 sm:gap-3 px-2 sm:px-4">
                        <div className="hidden shrink-0 items-center gap-2 rounded-full border border-primary/30 bg-white px-3 py-1.5 text-xs font-semibold text-primary shadow-sm sm:inline-flex">
                            <Megaphone className="h-3.5 w-3.5" />
                            Акции тарифов
                        </div>
                        <InfiniteSlider gap={16} duration={42} className="w-full">
                            {tariffAnnouncements.map((announcement, index) => (
                                <div
                                    key={`${announcement}-${index}`}
                                    className="inline-flex items-center gap-2 rounded-full border border-slate-200 bg-white px-3 py-1.5 sm:px-4 sm:py-2 text-[11px] sm:text-sm font-medium text-slate-700 shadow-sm"
                                >
                                    <BadgePercent className="h-4 w-4 text-primary" />
                                    <span className="whitespace-nowrap">{announcement}</span>
                                </div>
                            ))}
                        </InfiniteSlider>
                        <span className="hidden shrink-0 text-xs font-semibold text-primary/90 sm:inline">
                            Нажмите, чтобы открыть тарифы
                        </span>
                    </div>
                </div>
                <div className="container relative flex h-16 sm:h-20 items-center justify-between mx-auto px-3 sm:px-4 max-w-7xl">
                    <Link to="/" className="flex items-center gap-2 sm:gap-3 flex-shrink-0 min-w-0">
                        <div className="flex h-10 sm:h-16 items-center justify-center shrink-0">
                            <img src="/logo.png" alt="Opus" className="h-full w-auto object-contain" />
                        </div>
                        <span className="text-lg sm:text-2xl font-bold tracking-tight inline-block text-primary rubik-mono-one-regular ml-1">Анкеты</span>
                    </Link>

                    <div className="flex items-center gap-2 sm:hidden">
                        <div className="flex flex-col items-end text-[10px] sm:text-[11px] leading-[1.1] sm:leading-tight text-muted-foreground shrink-0 whitespace-nowrap">
                            <span>
                                Остаток: <span className="font-semibold text-foreground">{subscription?.cards_remaining ?? 0}</span>
                            </span>
                            {subscription?.daily_limit ? (
                                <span>
                                    Сегодня: <span className="font-semibold text-foreground">{subscription.daily_views_remaining ?? 0}/{subscription.daily_limit}</span>
                                </span>
                            ) : null}
                        </div>

                        <button
                            type="button"
                            onClick={() => setIsMobileMenuOpen((previous) => !previous)}
                            className="inline-flex sm:hidden h-10 w-10 items-center justify-center rounded-xl border border-border bg-card text-muted-foreground shadow-sm"
                            aria-label={isMobileMenuOpen ? "Закрыть меню" : "Открыть меню"}
                        >
                            {isMobileMenuOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
                        </button>
                    </div>

                    <nav className="hidden sm:flex items-center gap-3 sm:gap-6">
                        <div className="flex flex-col items-end text-[11px] leading-tight text-muted-foreground shrink-0 whitespace-nowrap">
                            <span>
                                Остаток: <span className="font-semibold text-foreground">{subscription?.cards_remaining ?? 0}</span>
                            </span>
                            {subscription?.daily_limit ? (
                                <span>
                                    Сегодня: <span className="font-semibold text-foreground">{subscription.daily_views_remaining ?? 0}/{subscription.daily_limit}</span>
                                </span>
                            ) : null}
                        </div>
                        <div className="h-6 w-px bg-border mx-1 sm:mx-2 hidden sm:block"></div>
                        <Link
                            to="/dashboard"
                            className={`flex items-center gap-2 text-xs sm:text-sm font-medium transition-colors hover:text-primary ${location.pathname === '/dashboard' || location.pathname === '/' ? 'text-primary' : 'text-muted-foreground'
                                }`}
                        >
                            <Users strokeWidth={2.5} className="w-4 h-4" />
                            <span className="hidden sm:inline-block">Анкеты</span>
                        </Link>
                        <Link
                            to="/tariffs"
                            className={`flex items-center gap-2 text-xs sm:text-sm font-medium transition-colors hover:text-primary ${location.pathname === '/tariffs' ? 'text-primary' : 'text-muted-foreground'
                                }`}
                        >
                            <CreditCard strokeWidth={2.5} className="w-4 h-4" />
                            <span className="hidden sm:inline-block">Тарифы</span>
                        </Link>
                        {isAuthenticated ? (
                            <div className="flex items-center gap-3 sm:gap-4">
                                <button
                                    onClick={() => setIsSettingsModalOpen(true)}
                                    className="text-xs sm:text-sm font-medium hover:text-primary transition-colors flex items-center gap-1.5 sm:gap-2"
                                >
                                    <span className="flex h-6 w-6 sm:h-7 sm:w-7 items-center justify-center rounded-full bg-muted">
                                        {userEmail?.[0]?.toUpperCase() || "U"}
                                    </span>
                                    <span className="hidden sm:inline-block">Кабинет</span>
                                </button>
                                <button onClick={logout} className="flex items-center gap-1.5 text-xs sm:text-sm font-medium text-muted-foreground hover:text-destructive transition-colors">
                                    <LogOut strokeWidth={2.5} className="w-4 h-4" />
                                    <span className="hidden sm:inline-block">Выйти</span>
                                </button>
                            </div>
                        ) : (
                            <button
                                onClick={() => setIsLoginModalOpen(true)}
                                className="flex items-center gap-2 bg-primary text-primary-foreground hover:bg-primary/90 px-3 py-1.5 sm:px-4 sm:py-2 rounded-lg text-xs sm:text-sm font-medium transition-colors"
                            >
                                <LogIn strokeWidth={2.5} className="w-4 h-4" />
                                Войти
                            </button>
                        )}
                    </nav>

                    {isMobileMenuOpen ? (
                        <div className="absolute right-3 top-[calc(100%-0.25rem)] z-50 w-[250px] rounded-2xl border border-border/80 bg-background/95 p-3 shadow-2xl backdrop-blur sm:hidden">
                            <div className="grid gap-2">
                                <Link
                                    to="/"
                                    className="flex items-center gap-2 rounded-xl px-3 py-2 text-sm font-medium hover:bg-muted"
                                >
                                    <Users className="h-4 w-4" />
                                    Анкеты
                                </Link>
                                <Link
                                    to="/tariffs"
                                    className="flex items-center gap-2 rounded-xl px-3 py-2 text-sm font-medium hover:bg-muted"
                                >
                                    <CreditCard className="h-4 w-4" />
                                    Тарифы
                                </Link>
                                {isAuthenticated ? (
                                    <>
                                        <button
                                            type="button"
                                            onClick={() => {
                                                setIsMobileMenuOpen(false);
                                                setIsSettingsModalOpen(true);
                                            }}
                                            className="flex items-center gap-2 rounded-xl px-3 py-2 text-left text-sm font-medium hover:bg-muted"
                                        >
                                            <Settings className="h-4 w-4" />
                                            Аккаунт
                                        </button>
                                        <button
                                            type="button"
                                            onClick={() => {
                                                setIsMobileMenuOpen(false);
                                                logout();
                                            }}
                                            className="flex items-center gap-2 rounded-xl px-3 py-2 text-left text-sm font-medium text-destructive hover:bg-destructive/10"
                                        >
                                            <LogOut className="h-4 w-4" />
                                            Выйти
                                        </button>
                                    </>
                                ) : (
                                    <button
                                        type="button"
                                        onClick={() => {
                                            setIsMobileMenuOpen(false);
                                            setIsLoginModalOpen(true);
                                        }}
                                        className="flex items-center gap-2 rounded-xl px-3 py-2 text-left text-sm font-medium hover:bg-muted"
                                    >
                                        <User className="h-4 w-4" />
                                        Войти
                                    </button>
                                )}
                            </div>
                        </div>
                    ) : null}
                </div>
            </header>

            <main className="flex-1 w-full max-w-7xl mx-auto p-3 sm:p-6 lg:p-8">
                <Outlet />
            </main>

            <footer className="border-t py-6 md:py-0">
                <div className="container flex flex-col items-center justify-between gap-4 md:h-16 md:flex-row mx-auto px-4 max-w-7xl text-sm text-muted-foreground">
                    <p>© 2026 Opus Platform. Все права защищены.</p>
                    <div className="flex gap-4">
                        <a href="#" className="hover:text-foreground transition-colors">Условия использования</a>
                        <a href="#" className="hover:text-foreground transition-colors">Политика конфиденциальности</a>
                    </div>
                </div>
            </footer>

            {/* Modals */}
            <LoginModal
                isOpen={isLoginModalOpen}
                onClose={() => setIsLoginModalOpen(false)}
            />

            <SettingsModal
                isOpen={isSettingsModalOpen}
                onClose={() => setIsSettingsModalOpen(false)}
                userEmail={userEmail || undefined}
            />
        </div>
    );
}
