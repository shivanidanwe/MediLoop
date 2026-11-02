import React, { useState, useRef } from 'react';
import { Box, IconButton, Tooltip, Paper, CircularProgress, Typography, Button } from '@mui/material';
import ZoomInIcon from '@mui/icons-material/ZoomIn';
import ZoomOutIcon from '@mui/icons-material/ZoomOut';
import RotateRightIcon from '@mui/icons-material/RotateRight';
import FullscreenIcon from '@mui/icons-material/Fullscreen';
import GetAppIcon from '@mui/icons-material/GetApp';
import RefreshIcon from '@mui/icons-material/Refresh';
import BrokenImageIcon from '@mui/icons-material/BrokenImage';
import PictureAsPdfIcon from '@mui/icons-material/PictureAsPdf';

const ImageViewer = ({ imageUrl, alt = 'Prescription Evidence', fileName = 'prescription.jpeg' }) => {
  const [scale, setScale] = useState(1);
  const [rotate, setRotate] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);
  const containerRef = useRef(null);

  const isPdf = Boolean(imageUrl && (imageUrl.toLowerCase().includes('.pdf') || (fileName && fileName.toLowerCase().endsWith('.pdf'))));

  const handleZoomIn = () => setScale((prev) => Math.min(prev + 0.3, 4));
  const handleZoomOut = () => setScale((prev) => Math.max(prev - 0.3, 0.5));
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
          console.error(`Error entering full-screen mode: ${err.message}`);
        });
      }
    }
  };

  const handleDownload = () => {
    if (!imageUrl) return;
    const downloadEndpoint = imageUrl.includes('?') ? `${imageUrl}&download=true` : `${imageUrl}?download=true`;
    const link = document.createElement('a');
    link.href = downloadEndpoint;
    link.download = fileName || `Prescription-${Date.now()}`;
    link.target = '_blank';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <Box ref={containerRef} sx={{ width: '100%', height: '100%', minHeight: 380, display: 'flex', flexDirection: 'column', bgcolor: '#0b1120', borderRadius: 3, overflow: 'hidden' }}>
      {/* Control Toolbar */}
      <Paper
        elevation={0}
        sx={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          px: 2,
          py: 1,
          bgcolor: 'rgba(15, 23, 42, 0.95)',
          borderBottom: '1px solid rgba(255, 255, 255, 0.1)',
          color: '#f8fafc'
        }}
      >
        <Typography variant="caption" sx={{ color: '#94a3b8', fontWeight: 600, display: 'flex', alignItems: 'center', gap: 0.8 }}>
          {isPdf ? <PictureAsPdfIcon sx={{ fontSize: 16, color: '#ef4444' }} /> : 'Original Scan'}
          {fileName}
        </Typography>

        <Box display="flex" gap={0.8} alignItems="center">
          {!isPdf && (
            <>
              <Tooltip title="Zoom In (Ctrl +)">
                <IconButton size="small" onClick={handleZoomIn} sx={{ color: '#e2e8f0', '&:hover': { bgcolor: 'rgba(255,255,255,0.1)' } }}>
                  <ZoomInIcon fontSize="small" />
                </IconButton>
              </Tooltip>
              <Tooltip title="Zoom Out (Ctrl -)">
                <IconButton size="small" onClick={handleZoomOut} sx={{ color: '#e2e8f0', '&:hover': { bgcolor: 'rgba(255,255,255,0.1)' } }}>
                  <ZoomOutIcon fontSize="small" />
                </IconButton>
              </Tooltip>
              <Tooltip title="Rotate 90°">
                <IconButton size="small" onClick={handleRotate} sx={{ color: '#e2e8f0', '&:hover': { bgcolor: 'rgba(255,255,255,0.1)' } }}>
                  <RotateRightIcon fontSize="small" />
                </IconButton>
              </Tooltip>
              <Tooltip title="Reset Zoom">
                <IconButton size="small" onClick={handleReset} sx={{ color: '#e2e8f0', '&:hover': { bgcolor: 'rgba(255,255,255,0.1)' } }}>
                  <RefreshIcon fontSize="small" />
                </IconButton>
              </Tooltip>
            </>
          )}
          <Tooltip title="Toggle Fullscreen">
            <IconButton size="small" onClick={handleFullscreen} sx={{ color: '#e2e8f0', '&:hover': { bgcolor: 'rgba(255,255,255,0.1)' } }}>
              <FullscreenIcon fontSize="small" />
            </IconButton>
          </Tooltip>
          <Tooltip title="Download Original File">
            <IconButton size="small" onClick={handleDownload} sx={{ color: '#38bdf8', '&:hover': { bgcolor: 'rgba(56, 189, 248, 0.15)' } }}>
              <GetAppIcon fontSize="small" />
            </IconButton>
          </Tooltip>
        </Box>
      </Paper>

      {/* Main Preview Area */}
      <Box
        sx={{
          flexGrow: 1,
          overflow: 'auto',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          position: 'relative',
          minHeight: 340,
          p: 2,
          bgcolor: '#030712'
        }}
      >
        {loading && !error && !isPdf && (
          <Box display="flex" flexDirection="column" alignItems="center" gap={1.5} position="absolute">
            <CircularProgress size={36} sx={{ color: '#38bdf8' }} />
            <Typography variant="caption" color="#94a3b8">
              Retrieving high-resolution prescription from secure database storage...
            </Typography>
          </Box>
        )}

        {error ? (
          <Box display="flex" flexDirection="column" alignItems="center" gap={1.5} p={3} textAlign="center">
            <BrokenImageIcon sx={{ fontSize: 48, color: '#f87171' }} />
            <Typography variant="body2" color="#f87171" fontWeight={700}>
              Prescription Evidence Unavailable
            </Typography>
            <Typography variant="caption" color="#94a3b8" maxWidth={360}>
              The original prescription file is not accessible on server storage. Never verify without authentic clinical evidence.
            </Typography>
            <Button
              variant="outlined"
              size="small"
              onClick={() => { setError(false); setLoading(true); }}
              sx={{ color: '#38bdf8', borderColor: '#0284c7', mt: 1, borderRadius: 2 }}
            >
              Retry Retrieval
            </Button>
          </Box>
        ) : isPdf ? (
          <Box sx={{ width: '100%', height: 480, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>
            <iframe
              src={imageUrl}
              title="PDF Prescription Viewer"
              width="100%"
              height="100%"
              style={{ border: 'none', borderRadius: 8 }}
            />
          </Box>
        ) : (
          <Box
            component="img"
            src={imageUrl}
            alt={alt}
            onLoad={() => setLoading(false)}
            onError={() => { setLoading(false); setError(true); }}
            sx={{
              maxWidth: '92%',
              maxHeight: '92%',
              objectFit: 'contain',
              transform: `scale(${scale}) rotate(${rotate}deg)`,
              transition: 'transform 0.18s ease-out',
              borderRadius: 2,
              boxShadow: '0 10px 30px rgba(0,0,0,0.6)',
              display: loading ? 'none' : 'block'
            }}
          />
        )}
      </Box>
    </Box>
  );
};

export default ImageViewer;
