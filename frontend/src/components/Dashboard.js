
import React, { useEffect, useState } from 'react';
import { 
    Container, 
    Typography, 
    Paper, 
    Table, 
    TableBody, 
    TableCell, 
    TableHead, 
    TableRow, 
    Chip, 
    Box, 
    Button, 
    Dialog, 
    DialogTitle, 
    DialogContent, 
    DialogActions,
    IconButton
} from '@mui/material';
import CloseIcon from '@mui/icons-material/Close';
import VisibilityIcon from '@mui/icons-material/Visibility';
import { getHistory } from '../services/api';
import PredictionResult from './PredictionResult';

const Dashboard = () => {
    const [history, setHistory] = useState([]);
    const [selectedAssessment, setSelectedAssessment] = useState(null);
    const [open, setOpen] = useState(false);

    useEffect(() => {
        const fetchHistory = async () => {
            try {
                const response = await getHistory();
                setHistory(response.data);
            } catch (error) {
                console.error("Failed to fetch history", error);
            }
        };
        fetchHistory();
    }, []);

    const handleOpen = (assessment) => {
        setSelectedAssessment(assessment);
        setOpen(true);
    };

    const handleClose = () => {
        setOpen(false);
        setSelectedAssessment(null);
    };

    return (
        <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
            <Typography variant="h4" gutterBottom sx={{ fontWeight: 700 }}>
                Your Assessment History
            </Typography>
            <Paper sx={{ p: 2, display: 'flex', flexDirection: 'column', borderRadius: 2 }}>
                <Table size="medium">
                    <TableHead>
                        <TableRow>
                            <TableCell sx={{ fontWeight: 600 }}>Date</TableCell>
                            <TableCell sx={{ fontWeight: 600 }}>Prediction</TableCell>
                            <TableCell sx={{ fontWeight: 600 }}>Probability</TableCell>
                            <TableCell sx={{ fontWeight: 600 }}>Status</TableCell>
                            <TableCell sx={{ fontWeight: 600 }} align="right">Actions</TableCell>
                        </TableRow>
                    </TableHead>
                    <TableBody>
                        {history.map((row) => (
                            <TableRow key={row.id} hover>
                                <TableCell>{new Date(row.timestamp).toLocaleString()}</TableCell>
                                <TableCell>{row.prediction}</TableCell>
                                <TableCell>{(row.probability * 100).toFixed(1)}%</TableCell>
                                <TableCell>
                                    <Chip
                                        label={row.prediction.includes("Pre") ? "Healthy" : "Attention Needed"}
                                        color={row.prediction.includes("Pre") ? "success" : "warning"}
                                        size="small"
                                    />
                                </TableCell>
                                <TableCell align="right">
                                    <Button 
                                        variant="outlined" 
                                        startIcon={<VisibilityIcon />}
                                        size="small"
                                        onClick={() => handleOpen(row)}
                                    >
                                        View Details
                                    </Button>
                                </TableCell>
                            </TableRow>
                        ))}
                        {history.length === 0 && (
                            <TableRow>
                                <TableCell colSpan={5} align="center" sx={{ py: 3 }}>
                                    <Typography variant="body2" color="text.secondary">
                                        No assessments found. Complete a questionnaire to see results here.
                                    </Typography>
                                </TableCell>
                            </TableRow>
                        )}
                    </TableBody>
                </Table>
            </Paper>

            {/* View Details Modal */}
            <Dialog 
                open={open} 
                onClose={handleClose}
                maxWidth="lg"
                fullWidth
                scroll="body"
            >
                <DialogTitle sx={{ m: 0, p: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <Typography variant="h5" sx={{ fontWeight: 700 }}>
                        Assessment Details
                    </Typography>
                    <IconButton
                        aria-label="close"
                        onClick={handleClose}
                        sx={{ color: (theme) => theme.palette.grey[500] }}
                    >
                        <CloseIcon />
                    </IconButton>
                </DialogTitle>
                <DialogContent dividers sx={{ bgcolor: '#f8f9fa' }}>
                    {selectedAssessment && (
                        <Box sx={{ py: 2 }}>
                            <PredictionResult result={selectedAssessment} />
                        </Box>
                    )}
                </DialogContent>
                <DialogActions sx={{ p: 2 }}>
                    <Button onClick={handleClose} variant="contained">
                        Close
                    </Button>
                </DialogActions>
            </Dialog>
        </Container>
    );
};

export default Dashboard;
