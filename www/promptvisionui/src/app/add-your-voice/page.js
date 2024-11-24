/* eslint-disable @next/next/no-img-element */
/* eslint-disable react/no-unescaped-entities */

'use client';
import React, { useState, useRef, useEffect } from 'react';
import styles from './AddYourVoice.module.css';
import { useRouter } from 'next/navigation';
import Image from 'next/image';

const AddYourVoicePage = () => {
  const router = useRouter();
  const [activeLanguage, setActiveLanguage] = useState('English');
  const [isRecording, setIsRecording] = useState(false);
  const [mediaRecorder, setMediaRecorder] = useState(null);
  const [recordedChunks, setRecordedChunks] = useState([]);
  const [elapsedTime, setElapsedTime] = useState(0); 
  const videoRef = useRef(null);
  const streamRef = useRef(null);
  const timerRef = useRef(null);
  const elapsedTimeRef = useRef(0);


  const handleGoBack = () => {
    router.back();
  };

  const handleLanguageSelect = (language) => {
    setActiveLanguage(language);
  };

  const handleStartRecording = () => {
    if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
      navigator.mediaDevices
        .getUserMedia({ video: true, audio: true })
        .then((mediaStream) => {
          streamRef.current = mediaStream;
          if (videoRef.current) {
            videoRef.current.srcObject = mediaStream;
          }

          const options = { mimeType: 'video/webm; codecs=vp9' };
          const mediaRec = new MediaRecorder(mediaStream, options);

          mediaRec.ondataavailable = (e) => {
            if (e.data && e.data.size > 0) {
              setRecordedChunks((prev) => [...prev, e.data]);
            }
          };

          mediaRec.start();
          setMediaRecorder(mediaRec);
          setIsRecording(true);
          startTimer(); // Start the timer immediately
        })
        .catch((err) => {
          console.error('Error accessing camera: ', err);
        });
    }
  };
  

   const handleStopRecording = () => {
    if (mediaRecorder) {
      mediaRecorder.stop();
      setIsRecording(false);
      stopTimer();

      if (streamRef.current) {
        streamRef.current.getTracks().forEach((track) => track.stop());
        streamRef.current = null;
      }

      if (videoRef.current) {
        videoRef.current.srcObject = null;
      }
    }
  };

  useEffect(() => {
    return () => {
      clearInterval(timerRef.current);
    };
  }, []);

  const startTimer = () => {
    elapsedTimeRef.current = 0; // Reset the ref
    setElapsedTime(0); // Reset the visible state
    clearInterval(timerRef.current); // Ensure no duplicate intervals
    timerRef.current = setInterval(() => {
      elapsedTimeRef.current += 1; // Update the ref
      setElapsedTime(elapsedTimeRef.current); // Update the state
    }, 1000); // Increment every second
  };

  const stopTimer = () => {
    clearInterval(timerRef.current);
    timerRef.current = null;
  };

  useEffect(() => {
    return () => {
      clearInterval(timerRef.current); // Cleanup on unmount
    };
  }, []);

  const formatTime = (time) => {
    const minutes = String(Math.floor(time / 60)).padStart(2, '0');
    const seconds = String(time % 60).padStart(2, '0');
    return `${minutes}:${seconds}`;
  };

  const downloadRecording = () => {
    const blob = new Blob(recordedChunks, { type: 'video/webm' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.style.display = 'none';
    a.href = url;
    a.download = 'recording.webm';
    document.body.appendChild(a);
    a.click();
    URL.revokeObjectURL(url); // Clean up the blob URL
  };

  return (
    <div className={styles.container}>
      <div className={styles.leftPanel}>
        <h1 className={styles.title}>
          Prompt
          <span>Vision</span>
        </h1>

       
        <div className={styles.videoContainer}>
          <video
            className={styles.video}
            ref={videoRef}
            autoPlay
            playsInline
            muted={!isRecording} // Mute the video unless recording
          />
        </div>
        {isRecording && (
          <div className={styles.recordingIndicator}>
            <div className={styles.redCircle}></div>
            <span className={styles.timer}>{formatTime(elapsedTime)}</span>
          </div>
          )}

        <div className={styles.buttonGroup}>
          <button className={styles.cancelButton} onClick={handleStopRecording}>
            <span>Stop</span>
          </button>
          <button className={styles.startRecordingButton} onClick={handleStartRecording}>
            <span>Start recording</span>
          </button>
          <button className={styles.startRecordingButton} onClick={downloadRecording}>
            <span>Save</span>
          </button>
        </div>
      </div>

      <div className={styles.rightPanel}>
        <h2 className={styles.rightTitle}>Add your face</h2>
        <p className={styles.rightDescription}>
          To add your face please record a video with your face well iluminated.
          P.S.: It'll take a while until your face is available. Please be patient.
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