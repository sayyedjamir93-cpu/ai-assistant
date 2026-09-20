import React, { useState, useRef } from "react";
import { AuthProvider } from "./context/AuthContext";
import Sidebar from "./components/Sidebar";
import Header from "./components/Header";
import AuthModal from "./components/AuthModal";

// Pages
import DashboardPage from "./pages/DashboardPage";
import ChatPage from "./pages/ChatPage";
import StudyPage from "./pages/StudyPage";
import CodingPage from "./pages/CodingPage";
import TasksPage from "./pages/TasksPage";
import NotesPage from "./pages/NotesPage";
import MemoryPage from "./pages/MemoryPage";
import ToolsPage from "./pages/ToolsPage";
import SettingsPage from "./pages/SettingsPage";

export default function App() {
  const [activeTab, setActiveTab] = useState("dashboard");
  const [activeMode, setActiveMode] = useState("normal"); // 'normal' | 'study' | 'coding'
  const [isAuthModalOpen, setIsAuthModalOpen] = useState(false);
  const [soundEnabled, setSoundEnabled] = useState(true);
  const currentAudioRef = useRef(null);

  // Global Audio Player for synthesized speech with immediate mute & cleanup support
  const handlePlayAudio = (audioBase64, onEndedCallback) => {
    if (!soundEnabled || !audioBase64) {
      if (onEndedCallback) onEndedCallback();
      return;
    }
    try {
      if (currentAudioRef.current) {
        currentAudioRef.current.pause();
        currentAudioRef.current.currentTime = 0;
      }
      const audio = new Audio(audioBase64);
      currentAudioRef.current = audio;
      audio.onended = () => {
        currentAudioRef.current = null;
        if (onEndedCallback) onEndedCallback();
      };
      audio.onerror = () => {
        currentAudioRef.current = null;
        if (onEndedCallback) onEndedCallback();
      };
      audio.play().catch((e) => {
        console.warn("Audio autoplay blocked by browser policy:", e);
        if (onEndedCallback) onEndedCallback();
      });
    } catch (e) {
      console.warn("Could not play audio:", e);
      if (onEndedCallback) onEndedCallback();
    }
  };

  const handleToggleSound = () => {
    setSoundEnabled((prev) => {
      const nextState = !prev;
      if (!nextState && currentAudioRef.current) {
        currentAudioRef.current.pause();
        currentAudioRef.current.currentTime = 0;
        currentAudioRef.current = null;
      }
      return nextState;
    });
  };

  const handleStopAudio = () => {
    if (currentAudioRef.current) {
      currentAudioRef.current.pause();
      currentAudioRef.current.currentTime = 0;
      currentAudioRef.current = null;
    }
  };

  const renderActivePage = () => {
    switch (activeTab) {
      case "dashboard":
        return (
          <DashboardPage
            activeMode={activeMode}
            setActiveMode={setActiveMode}
            setActiveTab={setActiveTab}
            onPlayAudio={handlePlayAudio}
            onStopAudio={handleStopAudio}
            soundEnabled={soundEnabled}
            onToggleSound={handleToggleSound}
          />
        );
      case "chat":
        return (
          <ChatPage
            activeMode={activeMode}
            setActiveMode={setActiveMode}
            onPlayAudio={handlePlayAudio}
            onStopAudio={handleStopAudio}
            soundEnabled={soundEnabled}
          />
        );
      case "study":
        return <StudyPage onPlayAudio={handlePlayAudio} soundEnabled={soundEnabled} onStopAudio={handleStopAudio} />;
      case "coding":
        return <CodingPage />;
      case "tasks":
        return <TasksPage />;
      case "notes":
        return <NotesPage />;
      case "memory":
        return <MemoryPage />;
      case "tools":
        return <ToolsPage onPlayAudio={handlePlayAudio} soundEnabled={soundEnabled} />;
      case "settings":
        return <SettingsPage soundEnabled={soundEnabled} onToggleSound={handleToggleSound} />;
      default:
        return (
          <DashboardPage
            activeMode={activeMode}
            setActiveMode={setActiveMode}
            setActiveTab={setActiveTab}
            onPlayAudio={handlePlayAudio}
            onStopAudio={handleStopAudio}
            soundEnabled={soundEnabled}
            onToggleSound={handleToggleSound}
          />
        );
    }
  };

  return (
    <AuthProvider>
      <div style={{ display: "flex", minHeight: "100vh", background: "var(--bg-dark)" }}>
        {/* Persistent Navigation Sidebar */}
        <Sidebar
          activeTab={activeTab}
          setActiveTab={setActiveTab}
          activeMode={activeMode}
          setActiveMode={setActiveMode}
        />

        {/* Main Content View */}
        <div style={{ flex: 1, display: "flex", flexDirection: "column", minWidth: 0 }}>
          <Header
            activeMode={activeMode}
            onOpenAuthModal={() => setIsAuthModalOpen(true)}
            soundEnabled={soundEnabled}
            onToggleSound={handleToggleSound}
            onStopAudio={handleStopAudio}
          />

          <main style={{ flex: 1, overflowY: "auto" }}>
            {renderActivePage()}
          </main>
        </div>

        {/* Login / Registration Modal */}
        <AuthModal
          isOpen={isAuthModalOpen}
          onClose={() => setIsAuthModalOpen(false)}
        />
      </div>
    </AuthProvider>
  );
}
