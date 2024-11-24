// components/LandingPage.js
"use client";
import React from 'react';
import { useRouter } from 'next/navigation';
import styles from './LandingPage.module.css'; 



const LandingPage = () => {
  const router = useRouter(); 

  const handleGetStarted = () => {
    router.push('/generate-video'); 
  };

  
  return (
    
    <div className={styles.container}>
      
      <div className={styles.content}>
        <h1 className={styles.title}>Prompt Vision</h1>
        
        <p className={styles.description}>
          Turn your any idea or document into an explanatory video based on target age,
          knowledge, avaiable time, etc Turn your any idea or document into an explanatory video based on target age,
          knowledge, avaiable time, etc Turn your any idea or document into an explanatory video based on target age,
          knowledge, avaiable time, etc Turn your any idea or document into an explanatory video based on target age,
          knowledge, avaiable time, etcTurn your any idea or document into an explanatory video based on target age,
          knowledge, avaiable time, etc
        </p>
        <div className={styles.buttons}>
          <button className={styles.startButton} onClick={handleGetStarted}>Get started</button>
          <button className={styles.knowTeamButton}>Know team!</button>
        </div>
      </div>
      <div className={styles.videoContainer}>
        
       
        <div className={styles.videoPlaceholder}>
          <span role="img" aria-label="video">🎥</span>
        </div>
      </div>
    </div>
  );
};
export default LandingPage;
