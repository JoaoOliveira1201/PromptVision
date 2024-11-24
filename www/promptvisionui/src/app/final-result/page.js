'use client';

import styles from './FinalResults.module.css';
import { useRouter } from 'next/navigation';
import React, { useState, useEffect } from 'react';

const FinalResultsPage = () => {
  const router = useRouter();
  const [videoUrl, setVideoUrl] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    // Function to fetch video URL from backend
    const fetchVideo = async () => {
      try {
        setLoading(true);
        // Replace with your actual API endpoint
        const response = await fetch('/api/get-generated-video');
        
        if (!response.ok) {
          throw new Error('Failed to fetch video');
        }

        const data = await response.json();
        setVideoUrl(data.videoUrl);
      } catch (err) {
        console.error('Error fetching video:', err);
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchVideo();
  }, []);

  const handleGoBack = () => {
    router.push('/generate-video');
  };

  const handleDownload = async () => {
    if (videoUrl) {
      try {
        const response = await fetch(videoUrl);
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'presentation-video.mp4'; // Or get filename from backend
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
      } catch (err) {
        console.error('Error downloading video:', err);
        // Handle download error (show message to user)
      }
    }
  };

  return (
    <div className={styles.container}>
      <div className={styles.leftPanel}>
        <h1 className={styles.title}>
          Prompt
          <span>Vision</span>
        </h1>

        <div className={styles.buttonGroup}>
          <button 
            className={styles.downloadButton}
            onClick={handleDownload}
            disabled={!videoUrl || loading}
          >
            <span>Download</span>
          </button>
          <button
            className={styles.downloadButton}
            onClick={handleGoBack}
          >
            <span>Go Back</span>
          </button>
        </div>
      </div>

      <div className={styles.rightPanel}>
        <img src="/planets.png" alt="Top Image" className={styles.topImage} />
        <div className={styles.videoContainer}>
          {loading ? (
            <div className={styles.loadingState}>
              <div className={styles.spinner}></div>
              <p>Loading your presentation video...</p>
            </div>
          ) : error ? (
            <div className={styles.errorState}>
              <p>Error loading video: {error}</p>
              <button onClick={() => window.location.reload()}>
                Try Again
              </button>
            </div>
          ) : videoUrl ? (
            <video
              className={styles.video}
              controls
              playsInline
              poster="/video-thumbnail.jpg" // Optional: Add a thumbnail while video loads
            >
              <source src={videoUrl} type="video/mp4" />
              Your browser does not support the video tag.
            </video>
          ) : (
            <div className={styles.noVideoState}>
              <p>No video available</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default FinalResultsPage;