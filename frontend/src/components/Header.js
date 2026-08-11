
import React, { useContext } from 'react';
import { AppBar, Toolbar, Typography, Button, Box } from '@mui/material';
import LocalHospitalIcon from '@mui/icons-material/LocalHospital';
import { Link, useNavigate } from 'react-router-dom';
import { AuthContext } from '../context/AuthContext';

const Header = () => {
  const { user, logout } = useContext(AuthContext);
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <AppBar position="static" elevation={2}>
      <Toolbar>
        <LocalHospitalIcon sx={{ mr: 2, fontSize: 30 }} />
        <Typography variant="h5" component="div" sx={{ flexGrow: 1, fontWeight: 600 }}>
          <Link to="/" style={{ color: 'white', textDecoration: 'none' }}>
            Menopause Detection
          </Link>
        </Typography>

        {user ? (
          <Box>
            <Button color="inherit" component={Link} to="/dashboard">Dashboard</Button>
            <Button color="inherit" component={Link} to="/questionnaire">New Assessment</Button>
            <Button color="inherit" onClick={handleLogout}>Logout</Button>
          </Box>
        ) : (
          <Box>
            <Button color="inherit" component={Link} to="/login">Login</Button>
            <Button color="inherit" component={Link} to="/register">Register</Button>
          </Box>
        )}
      </Toolbar>
    </AppBar>
  );
};

export default Header;
