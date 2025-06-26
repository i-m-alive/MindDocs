import React, { useState, useEffect } from 'react';
import './Footer.css';

function Footer() {
  const [isDark, setIsDark] = useState(() => localStorage.getItem('theme') === 'dark');
  const [showScroll, setShowScroll] = useState(false);

  useEffect(() => {
    const onScroll = () => setShowScroll(window.scrollY > 300);
    window.addEventListener('scroll', onScroll);
    return () => window.removeEventListener('scroll', onScroll);
  }, []);

  const toggleTheme = () => {
    const newTheme = isDark ? 'light' : 'dark';
    document.body.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
    setIsDark(!isDark);
  };

  const scrollToTop = () => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  useEffect(() => {
    document.body.setAttribute('data-theme', isDark ? 'dark' : 'light');
  }, [isDark]);

  return (
    <footer className={`footer ${isDark ? 'footer-dark' : 'footer-light'}`}>
    <div className="footer-inner d-flex flex-column flex-md-row justify-content-between align-items-center py-3 px-2">
        {/* Contact Info */}
        <div className="footer-left text-center text-md-start mb-2 mb-md-0">
        <p className="mb-1 fw-bold">👨‍💻 Kumar Shivraj Bhakat</p>
        <p className="mb-1">📞 <a href="tel:+918329788136" className="footer-link">+91 83297 88136</a></p>
        <p className="mb-0">📧 <a href="mailto:kumarshivrajbhakat@gmail.com" className="footer-link">kumarshivrajbhakat@gmail.com</a></p>
        </div>

        {/* Socials + Theme */}
        <div className="footer-right text-center text-md-end">
        <div className="mb-2">
            <a href="https://github.com/i-m-alive" target="_blank" rel="noreferrer" className="footer-link me-3">🌐 GitHub</a>
            <a href="https://www.linkedin.com/in/kumar-shivraj-bhakat-6403b7236" target="_blank" rel="noreferrer" className="footer-link">💼 LinkedIn</a>
        </div>
        <button className="btn btn-sm btn-outline-light" onClick={toggleTheme}>
            {isDark ? '☀️ Light Mode' : '🌙 Dark Mode'}
        </button>
        </div>
    </div>

    {showScroll && (
        <button className="scroll-to-top" onClick={scrollToTop} title="Back to Top">⬆️</button>
    )}
    </footer>

  );
}

export default Footer;
