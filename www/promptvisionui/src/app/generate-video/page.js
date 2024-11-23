/* eslint-disable @next/next/no-img-element */
// pages/generate-video.js
'use client';
import React, { useState } from 'react';
import { useRouter } from 'next/navigation';

import styles from './GenerateVideo.module.css'; 

const GenerateVideo = () => {
  const router = useRouter();

  const [isChecked, setIsChecked] = useState(false); // State to control the checkbox

  const handleCheckboxChange = () => {
    setIsChecked(!isChecked); // Toggle checkbox state
  };

  const handleLearnMoreClick = () => {
    router.push('/add-your-voice'); // Replace with the actual route to the page
  };

  const handleGenerate = () => {
    router.push('/final-result');
  };
  return (
    <div className={styles.container}>
     
      {/* Left Panel */}
      <div className={styles.leftPanel}>
        <h1 className={styles.title}>Prompt Vision</h1>
        <p className={styles.description}>
          Add your voice to become one of the teachers voices
        </p>
        <button className={styles.learnMoreButton} onClick={handleLearnMoreClick}>Learn more</button>
        <img 
    src="/rocket.png" 
    alt="Decorative Image" 
    className={styles.leftPanelImage}
  />
      </div>

      {/* Right Panel */}
      <div className={styles.rightPanel}>
      <div className={styles.contentWrapper}>
        <h2 className={styles.topicTitle}>Topic</h2>
        <div className={styles.topicInputs}>
          <button className={styles.fileButton}>Write the topic</button>
          <button className={styles.fileButton}>Drop your file</button>
        </div>

        <h2 className={styles.detailLevelTitle}>Detail level</h2>
        <div className={styles.detailLevelOptions}>
          <button className={styles.levelButton}>Basic</button>
          <button className={styles.levelButton }>Intermediate</button>
          <button className={styles.levelButton}>World class</button>
        </div>

        <h2 className={styles.voiceTitle}>Voice</h2>
        <div className={styles.languageOptions}>
          <button className={styles.languageButton}>English 🇬🇧</button>
          <button className={styles.languageButton}>Português 🇵🇹</button>
        </div>

        <div className={styles.options}>
          <label className={styles.optionLabel}>
          <input
                type="checkbox"
                checked={isChecked}
                onChange={handleCheckboxChange}
              />{'Subtitles '}
          </label>
          <select className={styles.voiceSelector}>
            <option>Default - Man</option>
            <option>Default - Woman</option>
          </select>
          <select className={styles.musicSelector}>
            <option>Background music</option>
          </select>
        </div>

        <button onClick={handleGenerate} className={styles.generateButton}>Generate</button>
      </div>
    </div>
    </div>
  );
};

export default GenerateVideo;
