import { useState, useEffect } from 'react';
import { Outlet, Link, useLocation, useNavigate } from 'react-router-dom';
import { BadgePercent, Megaphone } from 'lucide-react';
import { useAuth } from '../hooks/useAuth';
import { useSubscription } from '../hooks/useTariffs';
import LoginModal from './LoginModal';
import SettingsModal from './SettingsModal';
import { InfiniteSlider } from './ui/infinite-slider';

const tariffAnnouncements = [
    'Тариф Неделя: 25 контактов, до 15 в день — 1900 сом',
    'Тариф Месяц: 80 контактов, до 20 в день — 4900 сом',
    'Оплата проходит через Finik, ссылка формируется автоматически',
    'Продлите доступ заранее, чтобы не терять контакты кандидатов',
    'Нажмите на ленту, чтобы перейти к оплате тарифов',
];

export default function Layout() {
    const location = useLocation();
    const navigate = useNavigate();
    const { isAuthenticated, userEmail, logout } = useAuth();
    const { data: subscription } = useSubscription();

    const [isLoginModalOpen, setIsLoginModalOpen] = useState(false);
    const [isSettingsModalOpen, setIsSettingsModalOpen] = useState(false);

    useEffect(() => {
        const handleOpenLogin = () => setIsLoginModalOpen(true);
        window.addEventListener('openLoginModal', handleOpenLogin);
        return () => window.removeEventListener('openLoginModal', handleOpenLogin);
    }, []);

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
                <div className="container flex h-16 sm:h-20 items-center justify-between mx-auto px-3 sm:px-4 max-w-7xl">
                    <Link to="/" className="flex items-center gap-3 flex-shrink-0">
                        <div className="flex h-10 sm:h-16 items-center justify-center shrink-0">
                            <img src="/logo.png" alt="Opus" className="h-full w-auto object-contain" />
                        </div>
                        <span className="text-xl sm:text-2xl font-bold tracking-tight hidden sm:inline-block">Work</span>
                    </Link>

                    <nav className="flex items-center gap-3 sm:gap-6">
                        <Link
                            to="/dashboard"
                            className={`text-xs sm:text-sm font-medium transition-colors hover:text-primary ${location.pathname === '/dashboard' || location.pathname === '/' ? 'text-primary' : 'text-muted-foreground'
                                }`}
                        >
                            Сотрудники
                        </Link>
                        <Link
                            to="/tariffs"
                            className={`text-xs sm:text-sm font-medium transition-colors hover:text-primary ${location.pathname === '/tariffs' ? 'text-primary' : 'text-muted-foreground'
                                }`}
                        >
                            Тарифы
                        </Link>

                        <div className="h-6 w-px bg-border mx-1 sm:mx-2 hidden sm:block"></div>

                        {isAuthenticated ? (
                            <div className="flex items-center gap-3 sm:gap-4">
                                <span className="hidden md:inline text-xs text-muted-foreground">
                                    Остаток: <span className="font-semibold text-foreground">{subscription?.cards_remaining ?? 0}</span>
                                </span>
                                <button
                                    onClick={() => setIsSettingsModalOpen(true)}
                                    className="text-xs sm:text-sm font-medium hover:text-primary transition-colors flex items-center gap-1.5 sm:gap-2"
                                >
                                    <span className="flex h-6 w-6 sm:h-7 sm:w-7 items-center justify-center rounded-full bg-muted">
                                        {userEmail?.[0]?.toUpperCase() || "U"}
                                    </span>
                                    <span className="hidden sm:inline-block">Кабинет</span>
                                </button>
                                <button onClick={logout} className="text-xs sm:text-sm font-medium text-muted-foreground hover:text-destructive transition-colors">
                                    Выйти
                                </button>
                            </div>
                        ) : (
                            <button
                                onClick={() => setIsLoginModalOpen(true)}
                                className="bg-primary text-primary-foreground hover:bg-primary/90 px-3 py-1.5 sm:px-4 sm:py-2 rounded-md text-xs sm:text-sm font-medium transition-colors"
                            >
                                Войти
                            </button>
                        )}
                    </nav>
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
