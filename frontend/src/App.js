import React, { useEffect, useState } from 'react';
import { Routes, Route, useLocation } from 'react-router-dom';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import UploadPage from './pages/UploadPage';
import ChatbotPage from './pages/ChatbotPage';
import SummaryPage from './pages/SummaryPage';
import TranslationPage from './pages/TranslationPage';
import Navbar from './components/Navbar';
import DocumentListPage from './pages/DocumentListPage';
import HomePage from './pages/HomePage';
import Footer from './components/Footer';
import SplashScreen from './components/SplashScreen';

function App() {
  const [loading, setLoading] = useState(true);
  const location = useLocation();

  useEffect(() => {
    // Show splash screen on first load or route change
    setLoading(true);
    const timeout = setTimeout(() => setLoading(false), 1500); // .8 sec

    return () => clearTimeout(timeout);
  }, [location.pathname]);

  return (
    <>
      {loading && <SplashScreen />}
      {!loading && (
        <>
          <Navbar />
          <main className="flex-grow-1 w-100 d-flex justify-content-center">
            <Routes>
              <Route path="/" element={<HomePage />} />
              <Route path="/home" element={<HomePage />} />
              <Route path="/login" element={<LoginPage />} />
              <Route path="/register" element={<RegisterPage />} />
              <Route path="/upload" element={<UploadPage />} />
              <Route path="/documents" element={<DocumentListPage />} />
              <Route path="/chat" element={<ChatbotPage />} />
              <Route path="/summary" element={<SummaryPage />} />
              <Route path="/translate" element={<TranslationPage />} />
            </Routes>
          </main>
          <Footer />
        </>
      )}
    </>
  );
}

export default App;
