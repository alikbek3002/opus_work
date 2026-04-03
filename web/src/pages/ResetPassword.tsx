import { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { ensureSupabaseClient } from '@/lib/supabase';

export default function ResetPassword() {
    const navigate = useNavigate();
    const [password, setPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [isReady, setIsReady] = useState(false);
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');

    useEffect(() => {
        let isMounted = true;

        async function prepareRecoverySession() {
            try {
                const supabase = ensureSupabaseClient();
                const hashParams = new URLSearchParams(window.location.hash.replace(/^#/, ''));
                const accessToken = hashParams.get('access_token');
                const refreshToken = hashParams.get('refresh_token');
                const type = hashParams.get('type');

                if (!accessToken || !refreshToken || type !== 'recovery') {
                    throw new Error('Ссылка для сброса пароля недействительна или устарела.');
                }

                const { error: sessionError } = await supabase.auth.setSession({
                    access_token: accessToken,
                    refresh_token: refreshToken,
                });

                if (sessionError) {
                    throw sessionError;
                }

                window.history.replaceState({}, document.title, '/reset-password');
                if (isMounted) {
                    setIsReady(true);
                }
            } catch (err: any) {
                if (isMounted) {
                    setError(err.message || 'Не удалось открыть форму сброса пароля.');
                }
            }
        }

        void prepareRecoverySession();

        return () => {
            isMounted = false;
        };
    }, []);

    const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
        event.preventDefault();
        setError('');
        setSuccess('');

        if (password.length < 6) {
            setError('Пароль должен быть не короче 6 символов.');
            return;
        }

        if (password !== confirmPassword) {
            setError('Пароли не совпадают.');
            return;
        }

        setIsSubmitting(true);
        try {
            const supabase = ensureSupabaseClient();
            const { error: updateError } = await supabase.auth.updateUser({ password });
            if (updateError) {
                throw updateError;
            }

            await supabase.auth.signOut();
            localStorage.removeItem('access_token');
            localStorage.removeItem('user_id');
            localStorage.removeItem('user_email');
            window.dispatchEvent(new Event('auth_changed'));

            setSuccess('Пароль успешно обновлён. Теперь можно войти с новым паролем.');
            setTimeout(() => navigate('/'), 1200);
        } catch (err: any) {
            setError(err.message || 'Не удалось обновить пароль.');
        } finally {
            setIsSubmitting(false);
        }
    };

    return (
        <div className="mx-auto flex min-h-[70vh] max-w-md items-center px-4 py-10">
            <div className="w-full rounded-3xl border border-border/70 bg-card p-6 shadow-xl sm:p-8">
                <div className="mb-6 space-y-2 text-center">
                    <h1 className="text-2xl font-bold tracking-tight">Новый пароль</h1>
                    <p className="text-sm text-muted-foreground">
                        Задайте новый пароль для входа в кабинет.
                    </p>
                </div>

                {error ? (
                    <div className="mb-4 rounded-xl border border-destructive/20 bg-destructive/10 px-4 py-3 text-sm text-destructive">
                        {error}
                    </div>
                ) : null}

                {success ? (
                    <div className="mb-4 rounded-xl border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-700">
                        {success}
                    </div>
                ) : null}

                {isReady ? (
                    <form onSubmit={handleSubmit} className="space-y-4">
                        <div className="space-y-2">
                            <Label htmlFor="password">Новый пароль</Label>
                            <Input
                                id="password"
                                type="password"
                                value={password}
                                onChange={(event) => setPassword(event.target.value)}
                                placeholder="Минимум 6 символов"
                                required
                            />
                        </div>
                        <div className="space-y-2">
                            <Label htmlFor="confirmPassword">Повторите пароль</Label>
                            <Input
                                id="confirmPassword"
                                type="password"
                                value={confirmPassword}
                                onChange={(event) => setConfirmPassword(event.target.value)}
                                placeholder="Повторите новый пароль"
                                required
                            />
                        </div>
                        <Button type="submit" className="w-full" disabled={isSubmitting}>
                            {isSubmitting ? 'Сохраняем...' : 'Обновить пароль'}
                        </Button>
                    </form>
                ) : (
                    !error ? (
                        <div className="flex items-center justify-center py-8 text-sm text-muted-foreground">
                            Проверяем ссылку...
                        </div>
                    ) : null
                )}

                <div className="mt-6 text-center text-sm">
                    <Link to="/" className="font-medium text-primary hover:underline">
                        Вернуться на главную
                    </Link>
                </div>
            </div>
        </div>
    );
}
