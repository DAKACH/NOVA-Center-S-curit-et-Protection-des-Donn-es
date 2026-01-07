// Mobile menu
const toggle = document.querySelector('[data-nav-toggle]');
const links = document.querySelector('[data-nav-links]');
if (toggle && links) toggle.addEventListener('click', () => links.classList.toggle('open'));

// Active link highlight (no errors)
(function markActiveNav() {
  const path = location.pathname.split('/').pop() || 'index.html';
  document.querySelectorAll('.nav-links a').forEach(a => {
    const href = a.getAttribute('href');
    if (href === path) a.classList.add('active');
  });
})();

// Contact form - Envoi vers Flask Backend
const form = document.querySelector('#contactForm');
if (form) {
  const alertBox = document.querySelector('#formAlert');

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const name = form.name.value.trim();
    const email = form.email.value.trim();
    const message = form.message.value.trim();

    const emailOk = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);

    if (!name || !email || !message) return showAlert("Veuillez remplir tous les champs.", "err");
    if (!emailOk) return showAlert("Adresse email invalide.", "err");
    if (message.length < 10) return showAlert("Message trop court (minimum 10 caractères).", "err");

    // Envoi vers le backend Flask
    try {
      const response = await fetch('http://localhost:5000/inscription', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, email, message })
      });
      const result = await response.json();

      if (result.success) {
        showAlert("✅ " + result.message, "ok");
        form.reset();
      } else {
        showAlert("❌ " + result.message, "err");
      }
    } catch (error) {
      showAlert("❌ Erreur de connexion au serveur.", "err");
    }
  });

  function showAlert(msg, type) {
    alertBox.textContent = msg;
    alertBox.className = `alert show ${type}`;
  }
}
