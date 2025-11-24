const categoriesGrid = document.getElementById('categories-grid');
const overlay = document.getElementById('auth-overlay');
const usernameInput = document.getElementById('auth-username');
const passwordInput = document.getElementById('auth-password');
const registerBtn = document.getElementById('register-button');
const loginBtn = document.getElementById('login-button');
const statusEl = document.getElementById('auth-status');
const userStatus = document.getElementById('user-status');
const logoutBtn = document.getElementById('logout-button');

const fallbackCategories = [
    {
        name: 'Terminal',
        description: 'Simulate on-the-spot CLI tasks that validate navigation and command mastery.'
    },
    {
        name: 'Python Virtual Environments and Maven',
        description: 'Tackle mixed-environment workflows, from venv activation to Maven lifecycle knowledge.'
    },
    {
        name: 'Deploy on AWS',
        description: 'Walk through high-level deployment considerations and the services needed to ship safely.'
    }
];

const parseSkillTests = () => {
    const dataEl = document.getElementById('skill-tests-data');
    if (!dataEl) return [];
    try {
        const parsed = JSON.parse(dataEl.textContent);
        return Array.isArray(parsed) ? parsed : [];
    } catch (_err) {
        return [];
    }
};

const renderCategories = (items) => {
    categoriesGrid.innerHTML = '';
    items.forEach(({ id, name, description }) => {
        const card = document.createElement('article');
        card.className = 'card';
        const previewBtn = document.createElement('button');
        previewBtn.type = 'button';
        previewBtn.setAttribute('aria-label', `Open ${name} test preview`);
        previewBtn.textContent = 'Preview';
        previewBtn.addEventListener('click', () => {
            window.location.href = `/preview/${id}`;
        });
        card.innerHTML = `
                    <p class="card-eyebrow">Skill Test</p>
                    <h2>${name}</h2>
                    <p>${description}</p>
                `;
        card.appendChild(previewBtn);
        categoriesGrid.appendChild(card);
    });
};

const categories = (() => {
    const excluded = new Set(['File Type Identification']);
    const fromServer = parseSkillTests().filter(
        ({ name = '' }) => !excluded.has(name.trim())
    );
    const sanitizedFallback = fallbackCategories.filter(
        ({ name = '' }) => !excluded.has(name.trim())
    );
    return fromServer.length ? fromServer : sanitizedFallback;
})();

renderCategories(categories);

const setUser = (user) => {
    if (!user) return;
    localStorage.setItem('quizUser', JSON.stringify(user));
    userStatus.textContent = `Logged in as ${user.username}`;
    logoutBtn.removeAttribute('hidden');
};

const showOverlay = () => {
    overlay.removeAttribute('hidden');
    statusEl.textContent = '';
    passwordInput.value = '';
    usernameInput.focus();
    logoutBtn.setAttribute('hidden', '');
    userStatus.textContent = '';
};

const hideOverlay = () => {
    overlay.setAttribute('hidden', '');
    statusEl.textContent = '';
    passwordInput.value = '';
};

const apiBase = (() => {
    // If served from a static server (e.g., 5500), point to Flask on 8000
    if (location.port && location.port !== '8000') {
        return 'http://127.0.0.1:8000';
    }
    return '';
})();

const handleAuth = async (mode) => {
    const username = usernameInput.value.trim();
    const password = passwordInput.value;
    if (!username || !password) {
        statusEl.textContent = 'Both username and password are required.';
        return;
    }
    statusEl.textContent = mode === 'register' ? 'Registering...' : 'Logging in...';

    try {
        const response = await fetch(`${apiBase}/api/${mode}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });
        let payload = {};
        try {
            payload = await response.json();
        } catch (_parseErr) {
            // leave payload empty for error handling
        }
        if (!response.ok) {
            statusEl.textContent = payload.error || `Server error (${response.status}).`;
            return;
        }
        const { user } = payload;
        setUser(user);
        hideOverlay();
    } catch (_err) {
        statusEl.textContent = 'Network error. Please try again.';
    }
};

registerBtn.addEventListener('click', () => handleAuth('register'));
loginBtn.addEventListener('click', () => handleAuth('login'));

logoutBtn.addEventListener('click', async () => {
    try {
        await fetch(`${apiBase}/api/logout`, { method: 'POST', credentials: 'include' });
    } catch (_err) {
        // ignore network issues on logout
    }
    localStorage.removeItem('quizUser');
    showOverlay();
});

// Show modal on first visit; prefill username if stored
const storedUser = (() => {
    try {
        return JSON.parse(localStorage.getItem('quizUser') || 'null');
    } catch (_err) {
        return null;
    }
})();
if (storedUser) {
    usernameInput.value = storedUser.username;
    setUser(storedUser);
    hideOverlay();
} else {
    showOverlay();
}

