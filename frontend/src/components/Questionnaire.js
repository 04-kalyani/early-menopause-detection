
import React, { useState, useEffect } from 'react';
import { Container, Typography, Paper, Grid, TextField, Button, MenuItem, Box, Alert, Stack, Chip, Divider } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { getModelColumns, submitQuestionnaire } from '../services/api';

const Questionnaire = () => {
    const [columns, setColumns] = useState([]);
    const [answers, setAnswers] = useState({});
    const [error, setError] = useState('');
    const [result, setResult] = useState(null);
    const navigate = useNavigate();

    useEffect(() => {
        const fetchColumns = async () => {
            try {
                const response = await getModelColumns();
                setColumns(response.data.columns);
            } catch (err) {
                setError("Failed to load questionnaire fields.");
            }
        };
        fetchColumns();
    }, []);

    const getLabel = (col) => {
        const mappings = {
            'chronicd': 'Chronic Diseases',
            'DM': 'Diabetes Mellitus',
            'Increase Bp Thyroid gland': 'High BP / Thyroid',
            'Varcoise': 'Varicose Veins',
            'preventive': 'Preventive Care',
            'Respiratory': 'Respiratory Issues',
            'Tumors': 'Tumors / Cysts',
            'Constipation': 'Digestive Issues',
            'Back pain': 'Back Pain',
            'Heart disease': 'Heart Disease'
        };
        return mappings[col] || col;
    };

    const handleChange = (col, value) => {
        setAnswers({ ...answers, [col]: value });
    };

    const loadDemo = (type) => {
        let demoData = {};
        // Demo data based on SMOTE Model Feature Importance
        // Top features: 'I could not control my health', 'DM', 'Increase Bp Thyroid gland', 
        // 'preventive', 'I could control my important things', 'Age'

        if (type === 'pre') { // Healthy / Regular -> Class 1
            demoData = {
                'Age': 30,
                'I could not control my health': 1, // Low lack of control
                'DM': 0, 'Increase Bp Thyroid gland': 0, // No diseases
                'preventive': 1, // Takes preventive measures (assumed positive)
                'I could control my important things': 4, // High control
                'How do you evaluate your health status': 1, // Good (Assuming 1 is good, verify scale)
                'I expect good things to happen in my life': 4
            };
        } else if (type === 'peri') { // Irregular -> Class 2
            demoData = {
                'Age': 48,
                'I could not control my health': 3, // Moderate lack of control
                'DM': 0,
                'Increase Bp Thyroid gland': 1, // Thyroid issues common
                'preventive': 0,
                'I could control my important things': 2, // Low control
                'How do you evaluate your health status': 2,
                'I expect good things to happen in my life': 3
            };
        } else if (type === 'post') { // Stopped -> Class 3
            demoData = {
                'Age': 60,
                'I could not control my health': 4, // High lack of control
                'DM': 1, 'Increase Bp Thyroid gland': 1, // Multiple health issues
                'preventive': 0,
                'I could control my important things': 1, // Very low control
                'How do you evaluate your health status': 3,
                'I expect good things to happen in my life': 2
            };
        }
        setAnswers({ ...answers, ...demoData });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            const response = await submitQuestionnaire(answers);
            setResult(response.data);
        } catch (err) {
            setError("Failed to submit assessment.");
        }
    };

    if (result) {
        return (
            <Container maxWidth="md" sx={{ mt: 4 }}>
                <Paper elevation={3} sx={{ p: 4, textAlign: 'center' }}>
                    <Typography variant="h4" gutterBottom>Assessment Result</Typography>

                    <Box sx={{ my: 3 }}>
                        <Chip
                            label={result.prediction}
                            color={result.is_menopausal ? "warning" : "success"}
                            sx={{ fontSize: '1.5rem', py: 3, px: 2, borderRadius: 2 }}
                        />
                    </Box>

                    <Typography variant="body1" sx={{ mb: 2 }}>
                        Confidence: {(result.probability * 100).toFixed(1)}%
                    </Typography>

                    {result.top_features && result.top_features.length > 0 && (
                        <Box sx={{ mt: 4, textAlign: 'left' }}>
                            <Divider sx={{ mb: 2 }} />
                            <Typography variant="h6" gutterBottom>Why this result?</Typography>
                            <Typography variant="body2" color="textSecondary" sx={{ mb: 2 }}>
                                Top factors contributing to this prediction:
                            </Typography>
                            <Stack spacing={1}>
                                {result.top_features.map((feature, idx) => (
                                    <Box key={idx} sx={{ display: 'flex', justifyContent: 'space-between', bgcolor: '#f5f5f5', p: 1, borderRadius: 1 }}>
                                        <Typography variant="subtitle2">{feature.feature}</Typography>
                                        <Typography
                                            variant="subtitle2"
                                            color={feature.importance > 0 ? "secondary" : "primary"}
                                        >
                                            {feature.importance > 0 ? "+" : ""}
                                            {feature.importance.toFixed(4)} impact
                                        </Typography>
                                    </Box>
                                ))}
                            </Stack>
                        </Box>
                    )}

                    <Button variant="contained" sx={{ mt: 4 }} onClick={() => { setResult(null); setAnswers({}); }}>
                        Start New Assessment
                    </Button>
                    <Button variant="outlined" sx={{ mt: 4, ml: 2 }} onClick={() => navigate('/dashboard')}>
                        Go to Dashboard
                    </Button>
                </Paper>
            </Container>
        );
    }

    return (
        <Container maxWidth="md" sx={{ mt: 4, mb: 4 }}>
            <Paper elevation={3} sx={{ p: 4 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
                    <Typography variant="h4">
                        Health Questionnaire
                    </Typography>
                </Box>

                {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

                <form onSubmit={handleSubmit}>
                    <Grid container spacing={3}>
                        {columns.map((col) => {
                            // Simple heuristic for field types
                            const isYesNo = col.toLowerCase().startsWith('do you') ||
                                ['Increase Bp Thyroid gland', 'Back pain', 'DM', 'Heart disease', 'Varcoise', 'Constipation', 'Respiratory', 'Tumors', 'chronicd', 'chronicals', 'preventive'].includes(col);
                            const isLikert = col.length > 25; // Long questions are likely Likert 1-5

                            return (
                                <Grid item xs={12} sm={isLikert ? 12 : 6} key={col}>
                                    {isYesNo ? (
                                        <TextField
                                            select
                                            fullWidth
                                            label={getLabel(col)}
                                            value={answers[col] !== undefined ? answers[col] : ''}
                                            onChange={(e) => handleChange(col, e.target.value)}
                                        >
                                            <MenuItem value={1}>Yes</MenuItem>
                                            <MenuItem value={0}>No</MenuItem>
                                        </TextField>
                                    ) : (
                                        <TextField
                                            fullWidth
                                            type="number"
                                            label={getLabel(col)}
                                            value={answers[col] !== undefined ? answers[col] : ''}
                                            onChange={(e) => handleChange(col, e.target.value)}
                                            helperText={isLikert ? "Rate 1-5 (Strongly disagree to Strongly agree)" : ""}
                                        />
                                    )}
                                </Grid>
                            );
                        })}
                    </Grid>
                    <Box sx={{ mt: 4, display: 'flex', justifyContent: 'flex-end' }}>
                        <Button type="submit" variant="contained" size="large">
                            Submit Assessment
                        </Button>
                    </Box>
                </form>
            </Paper>
        </Container>
    );
};

export default Questionnaire;
