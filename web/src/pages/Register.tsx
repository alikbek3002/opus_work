import { FormEvent } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';

export default function Register() {
    const { register, loading, error, setError } = useAuth();

    const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
        e.preventDefault();
        const formData = new FormData(e.currentTarget);
        try {
            await register({
                full_name: formData.get('fullName') as string,
                email: formData.get('email') as string,
                password: formData.get('password') as string,
                company_name: (formData.get('companyName') as string) || undefined,
            });
        } catch {
            // Ошибка уже установлена в хуке
        }
    };

    return (
        <div className="auth-page">
            <div className="auth-card">
                <div className="auth-header">
                    <h1>Регистрация</h1>
                    <p>Создайте аккаунт работодателя</p>
                </div>

                {error && <div className="alert alert-error">{error}</div>}

                <form onSubmit={handleSubmit} className="auth-form">
                    <div className="form-group">
                        <label htmlFor="fullName">ФИО</label>
                        <input
                            id="fullName"
                            name="fullName"
                            type="text"
                            placeholder="Иван Иванов"
                            required
                        />
                    </div>

                    <div className="form-group">
                        <label htmlFor="companyName">Компания</label>
                        <input
                            id="companyName"
                            name="companyName"
                            type="text"
                            placeholder="Название компании (необязательно)"
                        />
                    </div>

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
                            placeholder="Минимум 6 символов"
                            required
                            minLength={6}
                        />
                    </div>

                    <button type="submit" className="btn btn-primary btn-full" disabled={loading}>
                        {loading ? 'Регистрация...' : 'Зарегистрироваться'}
                    </button>
                </form>

                <div className="auth-footer">
                    <p>
                        Уже есть аккаунт?{' '}
                        <Link to="/login">Войти</Link>
                    </p>
                </div>
            </div>
        </div>
    );
}
