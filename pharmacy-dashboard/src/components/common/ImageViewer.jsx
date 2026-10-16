import React, { useState, useRef } from 'react';
import { Box, IconButton, Tooltip, Paper } from '@mui/material';
import ZoomInIcon from '@mui/icons-material/ZoomIn';
import ZoomOutIcon from '@mui/icons-material/ZoomOut';
import RotateRightIcon from '@mui/icons-material/RotateRight';
import FullscreenIcon from '@mui/icons-material/Fullscreen';
import GetAppIcon from '@mui/icons-material/GetApp';
import RefreshIcon from '@mui/icons-material/Refresh';

const ImageViewer = ({ imageUrl, alt = 'Prescription Image' }) => {
  const [scale, setScale] = useState(1);
  const [rotate, setRotate] = useState(0);
  const containerRef = useRef(null);

  const handleZoomIn = () => setScale((prev) => Math.min(prev + 0.25, 3));
  const handleZoomOut = () => setScale((prev) => Math.max(prev - 0.25, 0.5));
  const handleRotate = () => setRotate((prev) => (prev + 90) % 360);
  const handleReset = () => {
    setScale(1);
    setRotate(0);
  };

  const handleFullscreen = () => {
    if (containerRef.current) {
      if (document.fullscreenElement) {
        document.exitFullscreen();
      } else {
        containerRef.current.requestFullscreen().catch((err) => {
          console.error(`Error attempting to enable full-screen mode: ${err.message}`);
        });
      }
    }
  };

  const handleDownload = () => {
    if (!imageUrl) return;
    const link = document.createElement('a');
    link.href = imageUrl;
    link.download = `Prescription-${Date.now()}.jpg`;
    link.target = '_blank';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <Box ref={containerRef} sx={{ width: '100%', height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* Control Bar */}
      <Paper
        elevation={0}
        sx={{
          display: 'flex',
          justifyContent: 'center',
          gap: 1,
          p: 1,
          bgcolor: 'grey.100',
          borderBottom: '1px solid',
          borderColor: 'divider',
          borderTopLeftRadius: 12,
          borderTopRightRadius: 12
        }}
      >
        <Tooltip title="Zoom In">
          <IconButton size="small" onClick={handleZoomIn}>
            <ZoomInIcon fontSize="small" />
          </IconButton>
        </Tooltip>
        <Tooltip title="Zoom Out">
          <IconButton size="small" onClick={handleZoomOut}>
            <ZoomOutIcon fontSize="small" />
          </IconButton>
        </Tooltip>
        <Tooltip title="Rotate 90°">
          <IconButton size="small" onClick={handleRotate}>
            <RotateRightIcon fontSize="small" />
          </IconButton>
        </Tooltip>
        <Tooltip title="Reset">
          <IconButton size="small" onClick={handleReset}>
            <RefreshIcon fontSize="small" />
          </IconButton>
        </Tooltip>
        <Tooltip title="Toggle Fullscreen">
          <IconButton size="small" onClick={handleFullscreen}>
            <FullscreenIcon fontSize="small" />
          </IconButton>
        </Tooltip>
        <Tooltip title="Download Image">
          <IconButton size="small" onClick={handleDownload}>
            <GetAppIcon fontSize="small" />
          </IconButton>
        </Tooltip>
      </Paper>

      {/* Image Display */}
      <Box
        sx={{
          flexGrow: 1,
          overflow: 'hidden',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          bgcolor: 'grey.900',
          position: 'relative',
          minHeight: 350,
          borderBottomLeftRadius: 12,
          borderBottomRightRadius: 12
        }}
      >
        <Box
          component="img"
          src={imageUrl}
          alt={alt}
          sx={{
            maxWidth: '90%',
            maxHeight: '90%',
            objectFit: 'contain',
            transform: `scale(${scale}) rotate(${rotate}deg)`,
            transition: 'transform 0.20s ease-out',
            boxShadow: 3
          }}
        />
      </Box>
    </Box>
  );
};

export default ImageViewer;
