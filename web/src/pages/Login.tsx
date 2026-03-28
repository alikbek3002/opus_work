import { FormEvent } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';

export default function Login() {
    const { login, loading, error, setError } = useAuth();

    const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
        e.preventDefault();
        const formData = new FormData(e.currentTarget);
        try {
            await login({
                email: formData.get('email') as string,
                password: formData.get('password') as string,
            });
        } catch {
            // Ошибка уже установлена в хуке
        }
    };

    return (
        <div className="auth-page">
            <div className="auth-card">
                <div className="auth-header">
                    <h1>Вход в Opus</h1>
                    <p>Войдите в свой аккаунт работодателя</p>
                </div>

                {error && <div className="alert alert-error">{error}</div>}

                <form onSubmit={handleSubmit} className="auth-form">
                    <div className="form-group">
                        <label htmlFor="email">Email</label>
                        <input
                            id="email"
                            name="email"
                            type="email"
                            placeholder="name@company.com"
                            required
                        />
                    </div>

                    <div className="form-group">
                        <label htmlFor="password">Пароль</label>
                        <input
                            id="password"
                            name="password"
                            type="password"
                            placeholder="••••••••"
                            required
                            minLength={6}
                        />
                    </div>

                    <button type="submit" className="btn btn-primary btn-full" disabled={loading}>
                        {loading ? 'Вхожу...' : 'Войти'}
                    </button>
                </form>

                <div className="auth-footer">
                    <p>
                        Нет аккаунта?{' '}
                        <Link to="/register">Зарегистрироваться</Link>
                    </p>
                </div>
            </div>
        </div>
    );
}
