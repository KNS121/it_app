document.addEventListener('DOMContentLoaded', function () {
    console.log("DOM fully loaded and parsed");

    // Проверка существования элементов перед добавлением обработчиков
    const loginForm = document.getElementById('login-form');
    const registrationForm = document.getElementById('registration-form');

    // Логирование найденных элементов
    if (loginForm) {
        console.log('Login form found.');
        loginForm.addEventListener('submit', async function (event) {
            event.preventDefault();
            clearAllErrors();
            if (!validateLoginForm()) return;
            await loginFunction(event);
        });

        addInputListeners({
            email: document.getElementById('email'),
            password: document.getElementById('password')
        });
    } else {
        console.error('Login form not found.');
    }

    if (registrationForm) {
        console.log('Registration form found.');
        registrationForm.addEventListener('submit', async function (event) {
            event.preventDefault();
            clearAllErrors();
            if (!validateRegistrationForm()) return;
            await regFunction(event);
        });

        addInputListeners({
            email: document.getElementById('email'),
            password: document.getElementById('password'),
            phone_number: document.getElementById('phone_number'),
            first_name: document.getElementById('first_name'),
            last_name: document.getElementById('last_name')
        });
    } else {
        console.error('Registration form not found.');
    }
});

function addInputListeners(elements) {
    if (elements.email) {
        elements.email.addEventListener('input', debounce(() => validateField('email'), 300));
    }

    if (elements.password) {
        elements.password.addEventListener('input', debounce(() => validateField('password'), 300));
    }

    if (elements.phone_number) {
        elements.phone_number.addEventListener('input', debounce(() => validateField('phone_number'), 300));
    }

    if (elements.first_name) {
        elements.first_name.addEventListener('input', debounce(() => validateField('first_name'), 300));
    }

    if (elements.last_name) {
        elements.last_name.addEventListener('input', debounce(() => validateField('last_name'), 300));
    }
}

async function loginFunction(event) {
    event.preventDefault();

    const form = document.getElementById('login-form');
    const formData = new FormData(form);
    const data = Object.fromEntries(formData.entries());

    if (!validateLoginForm()) {
        return;
    }

    try {
        const response = await fetch('/auth/login/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data),
        });

        if (!response.ok) {
            const errorData = await response.json();
            displayFormErrors(errorData.detail || "Ошибка входа");
            return;
        }

        const result = await response.json();
        if (result.message) {
            window.location.href = '/pages/profile';
        }
    } catch (error) {
        console.error('Ошибка:', error);
        displayFormErrors('Ошибка сети. Проверьте подключение к интернету.');
    }
}

async function regFunction(event) {
    console.log("Начало регистрации...");
    event.preventDefault();

    const form = document.getElementById('registration-form');
    const formData = new FormData(form);
    const data = Object.fromEntries(formData.entries());
    console.log("Данные формы:", data);

    if (!validateRegistrationForm()) {
        console.log("Валидация не пройдена");
        return;
    }

    try {
        console.log("Отправка запроса...");
        const response = await fetch('/auth/register/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data),
        });

        console.log("Ответ сервера:", response);
        if (!response.ok) {
            const errorData = await response.json();
            displayFormErrors(errorData.detail || "Ошибка регистрации");
            return;
        }

        window.location.href = '/pages/login';
    } catch (error) {
        console.error('Ошибка:', error);
        displayFormErrors('Ошибка сети. Проверьте подключение.');
    }
}

function validateField(field) {
    const value = document.getElementById(field)?.value.trim();
    const errorElement = document.getElementById(`${field}-error`);

    if (!errorElement) return false;

    errorElement.textContent = '';
    let isValid = true;

    if (field === 'email') {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!value) {
            errorElement.textContent = 'Email обязателен';
            isValid = false;
        } else if (!emailRegex.test(value)) {
            errorElement.textContent = 'Неверный формат email';
            isValid = false;
        }
    } else if (field === 'password') {
        if (!value) {
            errorElement.textContent = 'Пароль обязателен';
            isValid = false;
        } else if (value.length < 6) {
            errorElement.textContent = 'Минимум 6 символов';
            isValid = false;
        } else if (!/\d/.test(value)) {
            errorElement.textContent = 'Должна быть цифра';
            isValid = false;
        } else if (!/[A-Za-z]/.test(value)) {
            errorElement.textContent = 'Должна быть буква';
            isValid = false;
        }
    } else if (field === 'phone_number') {
        const phoneRegex = /^\+7\d{10,15}$/;
        if (!value) {
            errorElement.textContent = 'Телефон обязателен';
            isValid = false;
        } else if (!phoneRegex.test(value)) {
            errorElement.textContent = 'Формат: +7XXXXXXXXXX (10-15 цифр)';
            isValid = false;
        }
    } else if (field === 'first_name') {
        if (!value) {
            errorElement.textContent = 'Имя обязательно';
            isValid = false;
        } else if (value.length < 2) {
            errorElement.textContent = 'Минимум 2 символа';
            isValid = false;
        }
    } else if (field === 'last_name') {
        if (!value) {
            errorElement.textContent = 'Фамилия обязательна';
            isValid = false;
        } else if (value.length < 2) {
            errorElement.textContent = 'Минимум 2 символа';
            isValid = false;
        }
    }

    return isValid;
}

function validateLoginForm() {
    const fields = ['email', 'password'];
    let isFormValid = true;

    fields.forEach((field) => {
        if (!validateField(field)) {
            isFormValid = false;
        }
    });

    return isFormValid;
}

function validateRegistrationForm() {
    const fields = ['email', 'password', 'phone_number', 'first_name', 'last_name'];
    let isFormValid = true;

    fields.forEach((field) => {
        if (!validateField(field)) {
            isFormValid = false;
        }
    });

    return isFormValid;
}

function clearAllErrors() {
    const errorMessages = document.querySelectorAll('.error-message');
    errorMessages.forEach(error => error.textContent = '');
}

function debounce(func, delay) {
    let timeout;
    return (...args) => {
        clearTimeout(timeout);
        timeout = setTimeout(() => func(...args), delay);
    };
}

function displayFormErrors(errors) {
    const errorContainer = document.querySelector('.error-container');
    errorContainer.innerHTML = '';

    if (typeof errors === 'string') {
        const errorElement = document.createElement('p');
        errorElement.textContent = errors;
        errorElement.style.color = 'red';
        errorContainer.appendChild(errorElement);
    } else if (Array.isArray(errors)) {
        errors.forEach(error => {
            const errorElement = document.createElement('p');
            errorElement.textContent = error.msg || error;
            errorElement.style.color = 'red';
            errorContainer.appendChild(errorElement);
        });
    }
}
