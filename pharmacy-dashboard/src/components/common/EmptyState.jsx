import React from 'react';
import { Box, Typography, Button } from '@mui/material';
import InboxOutlinedIcon from '@mui/icons-material/InboxOutlined';

const EmptyState = ({
  icon: IconComponent = InboxOutlinedIcon,
  title = 'No records found',
  description = 'There is currently no data to display here.',
  actionLabel,
  onAction,
  height = '50vh'
}) => {
  return (
    <Box
      display="flex"
      flexDirection="column"
      alignItems="center"
      justifyContent="center"
      height={height}
      width="100%"
      p={3}
      textAlign="center"
      bgcolor="background.paper"
      borderRadius={3}
      border="1px dashed"
      borderColor="divider"
    >
      <Box
        sx={{
          p: 2,
          borderRadius: '50%',
          bgcolor: 'grey.50',
          color: 'text.secondary',
          mb: 2,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center'
        }}
      >
        <IconComponent sx={{ fontSize: 48, opacity: 0.8 }} />
      </Box>
      <Typography variant="h6" fontWeight={600} gutterBottom>
        {title}
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ maxW: 320, mb: actionLabel ? 3 : 0 }}>
        {description}
      </Typography>
      {actionLabel && onAction && (
        <Button variant="contained" color="primary" onClick={onAction} sx={{ borderRadius: 2, px: 3 }}>
          {actionLabel}
        </Button>
      )}
    </Box>
  );
};

export default EmptyState;
