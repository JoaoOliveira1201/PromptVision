/* eslint-disable @next/next/no-img-element */
/* eslint-disable react/no-unescaped-entities */

'use client';
import React, { useState } from 'react';
import styles from './AddYourVoice.module.css';
import { useRouter } from 'next/navigation';
import Image from 'next/image';

const AddYourVoicePage = () => {
  const router = useRouter();
  const [text, setText] = useState('');
  const [activeLanguage, setActiveLanguage] = useState('English');

  const handleGoBack = () => {
    router.back();
  };

  const handleTextChange = (e) => {
    setText(e.target.value);
  };

  const handleLanguageSelect = (language) => {
    setActiveLanguage(language);
  };

  return (
    <div className={styles.container}>
      <div className={styles.leftPanel}>
        <h1 className={styles.title}>
          Prompt
          <span>Vision</span>
        </h1>

        <div className={styles.languageOptions}>
           <button className={`${styles.languageButton} ${activeLanguage === 'English' ? styles.active : ''}`}
            onClick={() => handleLanguageSelect('English')} > English <img src="/ENG.png" alt="GB" className={styles.flag} />
           </button>
           <button className={`${styles.languageButton} ${activeLanguage === 'Português' ? styles.active : ''}`}
            onClick={() => handleLanguageSelect('Português')} > Português <img src="/PT.png" alt="PT" className={styles.flag} />
           </button>
        </div>

        <div className={styles.textContainer}>
          <textarea
            className={styles.textbox}
            value={text}
            onChange={handleTextChange}
            placeholder="Write here..."
          />
        </div>

        <div className={styles.buttonGroup}>
          <button className={styles.cancelButton}>
            <span>Cancel</span>
          </button>
          <button className={styles.startRecordingButton}>
            <span>Start recording</span>
          </button>
        </div>
      </div>

      <div className={styles.rightPanel}>
        <h2 className={styles.rightTitle}>Add your voice</h2>
        <p className={styles.rightDescription}>
          To add your voice please select the preferred language and read the text carefully. 
          The better you read the text, the better you'll sound! You can also give a name and an icon! 
          P.S.: It'll take a while until your voice is available. Please be patient.
        </p>
        <button className={styles.goBackButton} onClick={handleGoBack}>Go back</button>
        <img 
    src="/astronaut.png" 
    alt="Astronaut" 
    className={styles.astronautImage}
  />
      </div>
    </div>
  );
};

export default AddYourVoicePage;