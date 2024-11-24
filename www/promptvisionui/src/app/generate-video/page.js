// pages/generate-video.js
'use client';
import React, { useState, useRef } from 'react';
import { useRouter } from 'next/navigation';
import styles from './GenerateVideo.module.css';

const GenerateVideo = () => {
  const router = useRouter();
  const fileInputRef = useRef(null);

  // Form States
  const [isChecked, setIsChecked] = useState(false);
  const [selectedDetailLevel, setSelectedDetailLevel] = useState(null);
  const [activeLanguage, setActiveLanguage] = useState('English');
  const [inputNumber, setInputNumber] = useState('');
  const [selectedFileName, setSelectedFileName] = useState('');
  const [selectedVoice, setSelectedVoice] = useState('Default - Man');
  const [selectedMusic, setSelectedMusic] = useState('Background music');

  // Modal States
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [topicText, setTopicText] = useState('');
  const [savedTopic, setSavedTopic] = useState('');

  // API States
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  // File Handling
  const handleFileButtonClick = () => {
    fileInputRef.current.click();
  };

  const handleFileChange = (event) => {
    const file = event.target.files[0];
    if (file) {
      setSelectedFileName(file.name);
      const reader = new FileReader();
      reader.onload = (e) => {
        const content = e.target.result;
        setSavedTopic(content);
      };
      reader.readAsText(file);
    }
  };

  // Form Controls
  const handleCheckboxChange = () => {
    setIsChecked(!isChecked);
  };

  const handleDetailLevelClick = (level) => {
    setSelectedDetailLevel(level);
  };

  const handleLanguageSelect = (language) => {
    setActiveLanguage(language);
  };

  const handleInputChange = (event) => {
    const value = event.target.value;
    if (/^\d*$/.test(value)) {
      setInputNumber(value);
    }
  };

  // Modal Controls
  const handleModalOpen = () => {
    setIsModalOpen(true);
    setTopicText('');
  };

  const handleModalClose = () => {
    setIsModalOpen(false);
    setTopicText('');
  };

  const handleSaveTopic = () => {
    setSavedTopic(topicText);
    setIsModalOpen(false);
    setTopicText('');
  };

  // Navigation
  const handleLearnMoreClick = () => {
    router.push('/add-your-voice');
  };

  // Form Submission
  const handleGenerate = async () => {
    try {
      // Validation
      if (!inputNumber) {
        setError('Please enter a duration');
        return;
      }
      if (!selectedDetailLevel) {
        setError('Please select a detail level');
        return;
      }
      if (!savedTopic && !selectedFileName) {
        setError('Please provide either text or a file');
        return;
      }
  
      setIsLoading(true);
      setError(null);
  
      // Create FormData
      const formData = new FormData();
  
      if (selectedFileName && fileInputRef.current.files[0]) {
        formData.append('file', fileInputRef.current.files[0]);
      } else if (savedTopic) {
        formData.append('text', savedTopic);
      }
  
      formData.append('duration', inputNumber);
      formData.append('detail_level', selectedDetailLevel);
      formData.append('character', selectedVoice);
  
      // API call
      const response = await fetch('/api/generate-presentation', {
        method: 'POST',
        body: formData,
      });
  
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to generate presentation');
      }
  
      // Handle successful response
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
  
      // Trigger download
      const a = document.createElement('a');
      a.href = url;
      a.download = 'presentation.mp4';
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
  
      router.push('/final-result');
    } catch (err) {
      setError(err.message);
      console.error('Error generating presentation:', err);
    } finally {
      setIsLoading(false);
    }
  };
  

  return (
    <div className={styles.container}>
      {/* Left Panel */}
      <div className={styles.leftPanel}>
        <h1 className={styles.title}>Prompt Vision</h1>
        <p className={styles.description}>Add your face</p>
        <button className={styles.learnMoreButton} onClick={handleLearnMoreClick}>
          Learn more
        </button>
        <img src="/rocket.png" alt="Decorative Image" className={styles.leftPanelImage} />
      </div>

      {/* Right Panel */}
      <div className={styles.rightPanel}>
        <div className={styles.contentWrapper}>
          {/* Topic Section */}
          <h2 className={styles.topicTitle}>Topic</h2>
          <div className={styles.topicInputs}>
            <button className={styles.fileButton} onClick={handleModalOpen}>
              Write the topic
            </button>
            <input
              type="file"
              ref={fileInputRef}
              onChange={handleFileChange}
              accept=".txt"
              style={{ display: 'none' }}
            />
            <button className={styles.fileButton} onClick={handleFileButtonClick}>
              {selectedFileName || 'Drop your file'}
            </button>
          </div>

          {/* Detail Level Section */}
          <h2 className={styles.detailLevelTitle}>Detail level</h2>
          <div className={styles.detailLevelOptions}>
            {['Basic', 'Intermediate', 'World class'].map((level) => (
              <button
                key={level}
                className={`${styles.levelButton} ${
                  selectedDetailLevel === level ? styles.selected : ''
                }`}
                onClick={() => handleDetailLevelClick(level)}
              >
                {level}
              </button>
            ))}
          </div>

          {/* Duration Section */}
          <h2 className={styles.duration}>Enter the duration</h2>
          <div className={styles.durationContainer}>
            <input
              type="text"
              className={styles.numberInput}
              value={inputNumber}
              onChange={handleInputChange}
              placeholder="Enter duration in minutes"
            />
          </div>

          {/* Voice Section */}
          <h2 className={styles.voiceTitle}>Voice</h2>
          <div className={styles.languageOptions}>
            <button
              className={`${styles.languageButton} ${
                activeLanguage === 'English' ? styles.active : ''
              }`}
              onClick={() => handleLanguageSelect('English')}
            >
              English <img src="/ENG.png" alt="GB" className={styles.flag} />
            </button>
            <button
              className={`${styles.languageButton} ${
                activeLanguage === 'Português' ? styles.active : ''
              }`}
              onClick={() => handleLanguageSelect('Português')}
            >
              Português <img src="/PT.png" alt="PT" className={styles.flag} />
            </button>
          </div>

          {/* Options Section */}
          <div className={styles.options}>
            <label className={styles.optionLabel}>
              <input
                type="checkbox"
                checked={isChecked}
                onChange={handleCheckboxChange}
              />
              Subtitles
            </label>
            <select 
              className={styles.voiceSelector}
              value={selectedVoice}
              onChange={(e) => setSelectedVoice(e.target.value)}
            >
              <option>Default - Man</option>
              <option>Default - Woman</option>
            </select>
            <select 
              className={styles.musicSelector}
              value={selectedMusic}
              onChange={(e) => setSelectedMusic(e.target.value)}
            >
              <option>Background music</option>
            </select>
          </div>

          {/* Error Display */}
          {error && <div className={styles.error}>{error}</div>}

          {/* Generate Button */}
          <button
            onClick={handleGenerate}
            className={styles.generateButton}
            disabled={isLoading}
          >
            {isLoading ? 'Generating...' : 'Generate'}
          </button>
        </div>
      </div>

      {/* Modal */}
      {isModalOpen && (
        <div className={styles.modalOverlay}>
          <div className={styles.modal}>
            <h2>Write the Topic</h2>
            <textarea
              className={styles.modalTextarea}
              value={topicText}
              onChange={(e) => setTopicText(e.target.value)}
              placeholder="Enter your topic"
            />
            <div className={styles.modalActions}>
              <button className={styles.modalButton} onClick={handleModalClose}>
                Cancel
              </button>
              <button className={styles.modalButton} onClick={handleSaveTopic}>
                Save
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Loading Overlay */}
      {isLoading && (
        <div className={styles.loadingOverlay}>
          <div className={styles.spinner} />
          <p>Generating your presentation...</p>
        </div>
      )}
    </div>
  );
};

export default GenerateVideo;