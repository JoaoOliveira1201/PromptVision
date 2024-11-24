/* eslint-disable @next/next/no-img-element */
/* eslint-disable react/no-unescaped-entities */
'use client';

import styles from './FinalResults.module.css';
import { useRouter } from 'next/navigation';
import React, { useState, useRef } from 'react';

const FinalResultsPage = () => {
  const router = useRouter();


  const [backgroundColor, setBackgroundColor] = useState('#FF0000');
  const [mainColor, setMainColor] = useState('#0000FF');
  const [secondaryColor, setSecondaryColor] = useState('#800080');

   // Ref for the file input
   const fileInputRef = useRef(null);
   const audioInputRef = useRef(null);

  
 
   // Trigger the hidden file input when button is clicked
   const handleImageUploadClick = () => {
     fileInputRef.current.click();
   };
   const handleAudioUploadClick = () => {
    audioInputRef.current.click();
  };
 
   // Handle file selection (optional)
   const handleFileChange = (event) => {
     const files = event.target.files;
     console.log(files); // Do something with the files if needed
   };

   const handleAudioFileChange = (event) => {
    const files = event.target.files;
    console.log("Selected audio files:", files); // Do something with the audio files if needed
  };
  const handleGoBack = () => {
    router.push('/generate-video'); // Navigate to the '/generate-video' route
  };
 

  return (
    <div className={styles.container}>
      <div className={styles.leftPanel}>
        <h1 className={styles.title}>
          Prompt
          <span>Vision</span>
        </h1>

        <div className={styles.section}>
      <h3 className={styles.sectionTitle}>Colors</h3>
      <div className={styles.colorGroups}>
        <div className={styles.colorGroup}>
          <span>Background</span>
          <div className={styles.colorDotSquare} style={{ backgroundColor }}></div>
          <input
            type="color"
            value={backgroundColor}
            onChange={(e) => setBackgroundColor(e.target.value)}
            className={styles.colorPickerCircle}
          />
        </div>
        <div className={styles.colorGroup}>
          <span>Main colors</span>
          <div className={styles.colorDotSquare} style={{ backgroundColor: mainColor }}></div>
          <input
            type="color"
            value={mainColor}
            onChange={(e) => setMainColor(e.target.value)}
            className={styles.colorPickerCircle}
          />
        </div>
        <div className={styles.colorGroup}>
          <span>Secondary colors</span>
          <div className={styles.colorDotSquare} style={{ backgroundColor: secondaryColor }}></div>
          <input
            type="color"
            value={secondaryColor}
            onChange={(e) => setSecondaryColor(e.target.value)}
            className={styles.colorPickerCircle}
          />
        </div>
      </div>
    </div>

        <div className={styles.section}>
          <h3 className={styles.sectionTitle}>Images</h3>
          <button className={styles.dropButton}  onClick={handleImageUploadClick}>
            Drop your custom images
          </button>
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileChange}
            style={{ display: 'none' }}
            accept="image/*" // Only allows image files
          />
        </div>

        <div className={styles.section}>
          <h3 className={styles.sectionTitle}>Sound</h3>
          <button className={styles.dropButton} onClick={handleAudioUploadClick}>
            Drop your custom soundtrack
          </button>
          <input
            type="file"
            ref={audioInputRef}
            onChange={handleAudioFileChange}
            style={{ display: 'none' }}
            accept="audio/mp3" // Only allows mp3 audio files
          />
        </div>

        <div className={styles.buttonGroup}>
          <button className={styles.redoButton}>
            <span>Redo</span>
          </button>
          <button className={styles.downloadButton}>
            <span>Download</span>
          </button>
          <button
            className={styles.downloadButton}
            onClick={handleGoBack} // Attach the go-back handler
          >
            <span>Go Back</span>
          </button>
        </div>
      </div>

      <div className={styles.rightPanel}>
      <img src="/planets.png" alt="Top Image" className={styles.topImage} />
        <div className={styles.videoPlaceholder}>
          <div className={styles.videoIcon}>📹</div>
        </div>
    
      </div>
    </div>
  );
};

export default FinalResultsPage;