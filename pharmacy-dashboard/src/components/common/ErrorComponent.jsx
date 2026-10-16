import React from 'react';
import { Box, Typography, Button } from '@mui/material';
import ErrorOutlineIcon from '@mui/icons-material/ErrorOutline';

const ErrorComponent = ({
  message = 'An unexpected error occurred while loading this section.',
  onRetry
}) => {
  return (
    <Box
      display="flex"
      flexDirection="column"
      alignItems="center"
      justifyContent="center"
      p={4}
      textAlign="center"
      width="100%"
      height="40vh"
      gap={2}
    >
      <ErrorOutlineIcon color="error" sx={{ fontSize: 56 }} />
      <Typography variant="h6" fontWeight={600} color="text.primary">
        Oops, something went wrong
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ maxWidth: 400 }}>
        {message}
      </Typography>
      {onRetry && (
        <Button variant="outlined" color="primary" onClick={onRetry} sx={{ mt: 1, borderRadius: 2 }}>
          Try Again
        </Button>
      )}
    </Box>
  );
};

export default ErrorComponent;
