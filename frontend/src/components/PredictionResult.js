import React, { useState } from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  Chip,
  Grid,
  LinearProgress,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Alert,
  Paper,
  Tooltip,
  Collapse,
  IconButton,
} from '@mui/material';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import CancelIcon from '@mui/icons-material/Cancel';
import RestaurantIcon from '@mui/icons-material/Restaurant';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import LocalDiningIcon from '@mui/icons-material/LocalDining';
import InfoIcon from '@mui/icons-material/Info';
import HelpOutlineIcon from '@mui/icons-material/HelpOutline';
import ExpandMore from '@mui/icons-material/ExpandMore';
import ExpandLess from '@mui/icons-material/ExpandLess';

import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip as RechartsTooltip, 
  ResponsiveContainer, 
  Cell,
  ReferenceLine
} from 'recharts';
import AssessmentIcon from '@mui/icons-material/Assessment';

const PredictionResult = ({ result }) => {
  const probability = result.probability || 0;
  const isMenopausal = result.is_menopausal;
  const confidence = result.confidence || 'moderate';
  const topFeatures = result.top_features || [];
  const baseValue = result.base_value || 0;
  const [showExplanations, setShowExplanations] = useState(false);

  const getConfidenceColor = (conf) => {
    switch (conf) {
      case 'high':
        return 'error';
      case 'moderate':
        return 'warning';
      case 'low':
        return 'info';
      default:
        return 'default';
    }
  };

  const getConfidenceText = (conf) => {
    switch (conf) {
      case 'high':
        return 'High Confidence';
      case 'moderate':
        return 'Moderate Confidence';
      case 'low':
        return 'Low Confidence';
      default:
        return 'Unknown';
    }
  };

  const getConfidenceExplanation = (conf) => {
    switch (conf) {
      case 'high':
        return 'The model is very certain about this prediction based on your age, symptoms, and health indicators.';
      case 'moderate':
        return 'The model is somewhat certain, but some factors may need further evaluation by a healthcare provider.';
      case 'low':
        return 'The model has lower certainty. Please consult with a healthcare provider for a more accurate assessment.';
      default:
        return 'Confidence level could not be determined.';
    }
  };

  const getStatusExplanation = (isMenopausal) => {
    if (isMenopausal) {
      return 'Menopause is the natural end of menstrual periods. This typically occurs around age 45-55. You may be experiencing perimenopause (transition phase) or postmenopause (12+ months without periods).';
    } else {
      return 'Premenopause means you are still having regular menstrual periods and have not yet entered the menopause transition. Your hormones are typically at normal levels.';
    }
  };

  const recommendations = result.recommendations || {};
  const hasRecommendations = 
    (recommendations.primary && recommendations.primary.length > 0) ||
    (recommendations.symptom_specific && Object.keys(recommendations.symptom_specific).length > 0) ||
    (recommendations.general_health && recommendations.general_health.length > 0);

  // Format symptom names for display
  const formatSymptomName = (symptom) => {
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
    
    if (mappings[symptom]) return mappings[symptom];
    
    return symptom
      .split('_')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  };

  return (
    <Box>
      {/* Main Prediction Card */}
      <Card 
        variant="outlined" 
        sx={{ 
          mb: 3, 
          bgcolor: isMenopausal ? 'error.light' : 'success.light',
          background: isMenopausal 
            ? 'linear-gradient(135deg, #ffebee 0%, #ffffff 100%)'
            : 'linear-gradient(135deg, #e8f5e9 0%, #ffffff 100%)',
        }}
      >
        <CardContent>
          <Grid container spacing={3} alignItems="center">
            <Grid item xs={12} sm={2}>
              <Box sx={{ display: 'flex', justifyContent: 'center' }}>
                {isMenopausal ? (
                  <CancelIcon 
                    sx={{ 
                      fontSize: 60, 
                      color: 'error.main',
                      bgcolor: 'white',
                      borderRadius: '50%',
                      p: 1,
                      boxShadow: 2
                    }} 
                  />
                ) : (
                  <CheckCircleIcon 
                    sx={{ 
                      fontSize: 60, 
                      color: 'success.main',
                      bgcolor: 'white',
                      borderRadius: '50%',
                      p: 1,
                      boxShadow: 2
                    }} 
                  />
                )}
              </Box>
            </Grid>
            
            <Grid item xs={12} sm={10}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                <Typography variant="h4" component="div" sx={{ fontWeight: 700 }}>
                  {isMenopausal ? 'Menopause Detected' : 'Premenopausal Status'}
                </Typography>
                <Tooltip 
                  title={getStatusExplanation(isMenopausal)}
                  arrow
                  placement="top"
                >
                  <IconButton size="small" sx={{ color: 'text.secondary' }}>
                    <HelpOutlineIcon fontSize="small" />
                  </IconButton>
                </Tooltip>
              </Box>
              
              <Typography variant="body2" color="text.secondary" sx={{ mb: 2, fontStyle: 'italic' }}>
                {getStatusExplanation(isMenopausal)}
              </Typography>
              
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                <Chip
                  label={getConfidenceText(confidence)}
                  color={getConfidenceColor(confidence)}
                  size="medium"
                  sx={{ fontWeight: 600 }}
                />
                <Tooltip 
                  title={getConfidenceExplanation(confidence)}
                  arrow
                  placement="top"
                >
                  <IconButton size="small" sx={{ color: 'text.secondary' }}>
                    <HelpOutlineIcon fontSize="small" />
                  </IconButton>
                </Tooltip>
              </Box>
              
              <Paper 
                variant="outlined" 
                sx={{ 
                  p: 2, 
                  mb: 2, 
                  bgcolor: 'grey.50',
                  borderLeft: '4px solid',
                  borderColor: probability > 0.5 ? 'error.main' : 'success.main'
                }}
              >
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Typography variant="body1" sx={{ fontWeight: 600 }}>
                      Prediction Probability
                    </Typography>
                    <Tooltip 
                      title={
                        isMenopausal 
                          ? `This percentage shows how likely you are to be in menopause based on your information. ${(probability * 100).toFixed(1)}% means the model predicts ${(probability * 100).toFixed(1)} out of 100 similar cases would be menopausal.`
                          : `This percentage shows the model's estimate of menopause likelihood. ${(probability * 100).toFixed(1)}% means a ${(probability * 100).toFixed(1)}% chance of being menopausal, which translates to a ${(100 - probability * 100).toFixed(1)}% chance of being premenopausal.`
                      }
                      arrow
                      placement="top"
                    >
                      <IconButton size="small" sx={{ color: 'text.secondary' }}>
                        <HelpOutlineIcon fontSize="small" />
                      </IconButton>
                    </Tooltip>
                  </Box>
                  <Typography variant="h5" sx={{ fontWeight: 700, color: probability > 0.5 ? 'error.main' : 'success.main' }}>
                    {(probability * 100).toFixed(1)}%
                  </Typography>
                </Box>
                <LinearProgress
                  variant="determinate"
                  value={probability * 100}
                  sx={{ 
                    height: 14, 
                    borderRadius: 7, 
                    bgcolor: 'grey.200',
                    '& .MuiLinearProgress-bar': {
                      borderRadius: 7,
                    }
                  }}
                  color={probability > 0.5 ? 'error' : 'success'}
                />
                <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
                  {isMenopausal 
                    ? `The model estimates a ${(probability * 100).toFixed(1)}% probability that you are experiencing menopause.`
                    : `The model estimates a ${(100 - probability * 100).toFixed(1)}% probability that you are premenopausal (not in menopause).`
                  }
                </Typography>
              </Paper>
              
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Typography variant="body2" color="text.secondary">
                  Prediction Model: <strong>{result.model_used || 'Super Learner'}</strong>
                </Typography>
                <Tooltip 
                  title="Super Learner is an advanced machine learning model that combines multiple prediction methods (LDA, QDA, Random Forest) to provide the most accurate results. It's like asking multiple medical experts and combining their opinions for better accuracy."
                  arrow
                  placement="top"
                >
                  <IconButton size="small" sx={{ color: 'text.secondary' }}>
                    <HelpOutlineIcon fontSize="small" />
                  </IconButton>
                </Tooltip>
              </Box>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* SHAP Feature Importance Section */}
      {topFeatures.length > 0 && (
        <Card variant="outlined" sx={{ mb: 3 }}>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 2, gap: 1 }}>
              <AssessmentIcon color="primary" />
              <Typography variant="h6" sx={{ fontWeight: 600 }}>
                Model Explanation (XAI)
              </Typography>
              <Tooltip title="This chart shows how different factors pushed the model's prediction from its starting point (base value) to the final result using SHAP (SHapley Additive exPlanations)." arrow>
                <IconButton size="small"><InfoIcon fontSize="small" /></IconButton>
              </Tooltip>
            </Box>
            
            <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
              Factors that pushed the prediction up (Red) or down (Green):
            </Typography>

            <Box sx={{ height: 400, width: '100%' }}>
              <ResponsiveContainer>
                <BarChart
                  data={topFeatures}
                  layout="vertical"
                  margin={{ top: 5, right: 30, left: 40, bottom: 5 }}
                >
                  <CartesianGrid strokeDasharray="3 3" horizontal={false} />
                  <XAxis type="number" hide />
                  <YAxis 
                    dataKey="feature" 
                    type="category" 
                    width={150}
                    tick={{ fontSize: 12 }}
                    tickFormatter={(val) => val.split('_').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ')}
                  />
                  <RechartsTooltip 
                    formatter={(value) => [value.toFixed(4), "Impact"]}
                    labelFormatter={(label) => `Factor: ${label}`}
                  />
                  <ReferenceLine x={0} stroke="#000" />
                  <Bar dataKey="importance">
                    {topFeatures.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.importance > 0 ? '#ef5350' : '#66bb6a'} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </Box>
            
            <Box sx={{ mt: 2, p: 2, bgcolor: 'grey.50', borderRadius: 1 }}>
              <Typography variant="caption" color="text.secondary" display="block">
                <strong>Base Value:</strong> {baseValue.toFixed(4)} (The average prediction of the model)
              </Typography>
              <Typography variant="caption" color="text.secondary" display="block">
                <strong>How to read:</strong> Factors in Red increase the likelihood of menopause, while Green factors decrease it.
              </Typography>
            </Box>
          </CardContent>
        </Card>
      )}

      {/* Detailed Explanations Section */}
      <Card variant="outlined" sx={{ mb: 3, bgcolor: 'grey.50' }}>
        <CardContent>
          <Box 
            sx={{ 
              display: 'flex', 
              alignItems: 'center', 
              justifyContent: 'space-between',
              cursor: 'pointer',
              '&:hover': { bgcolor: 'grey.100' },
              p: 1,
              borderRadius: 1
            }}
            onClick={() => setShowExplanations(!showExplanations)}
          >
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <InfoIcon color="primary" />
              <Typography variant="h6" sx={{ fontWeight: 600 }}>
                Understanding Your Results
              </Typography>
            </Box>
            {showExplanations ? <ExpandLess /> : <ExpandMore />}
          </Box>
          
          <Collapse in={showExplanations}>
            <Box sx={{ mt: 2, pl: 1 }}>
              <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 1, color: 'primary.main' }}>
                What does "{isMenopausal ? 'Menopause Detected' : 'Premenopausal Status'}" mean?
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 2, pl: 2 }}>
                {getStatusExplanation(isMenopausal)}
              </Typography>
              
              <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 1, color: 'primary.main' }}>
                What does "{getConfidenceText(confidence)}" mean?
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 2, pl: 2 }}>
                {getConfidenceExplanation(confidence)}
                <br />
                <strong>High:</strong> Very certain about the prediction
                <br />
                <strong>Moderate:</strong> Somewhat certain, may need professional evaluation
                <br />
                <strong>Low:</strong> Less certain, professional consultation recommended
              </Typography>
              
              <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 1, color: 'primary.main' }}>
                What does "Prediction Probability {(probability * 100).toFixed(1)}%" mean?
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 2, pl: 2 }}>
                This number shows how likely the model thinks you are to be in menopause based on your information.
                <br />
                • <strong>For menopause:</strong> {(probability * 100).toFixed(1)}% means out of 100 people with similar information, the model predicts {(probability * 100).toFixed(1)} would be menopausal.
                <br />
                • <strong>For premenopause:</strong> {(100 - probability * 100).toFixed(1)}% means the model thinks there's a {(100 - probability * 100).toFixed(1)}% chance you are still premenopausal.
                <br />
                • <strong>Lower percentage (0-30%):</strong> Very unlikely to be menopausal
                <br />
                • <strong>Medium percentage (30-70%):</strong> Transition phase, could be perimenopause
                <br />
                • <strong>Higher percentage (70-100%):</strong> More likely to be menopausal
              </Typography>
              
              <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 1, color: 'primary.main' }}>
                What is "Super Learner" model?
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 2, pl: 2 }}>
                Super Learner is an advanced prediction system that combines multiple machine learning methods:
                <br />
                • <strong>LDA (Linear Discriminant Analysis):</strong> Analyzes patterns in your data
                <br />
                • <strong>QDA (Quadratic Discriminant Analysis):</strong> Looks at more complex relationships
                <br />
                • <strong>Random Forest:</strong> Uses decision trees to make predictions
                <br />
                <br />
                By combining all three methods, Super Learner provides more accurate and reliable predictions than using any single method alone. It's like getting a second (and third) opinion from different medical experts.
              </Typography>
            </Box>
          </Collapse>
        </CardContent>
      </Card>

      {/* Interpretation Alert */}
      <Alert 
        severity={isMenopausal ? 'warning' : 'info'} 
        sx={{ mb: 3 }}
        icon={<InfoIcon />}
      >
        <Typography variant="body1" sx={{ fontWeight: 600, mb: 0.5 }}>
          What This Means For You:
        </Typography>
        {isMenopausal 
          ? `Based on your information, there is a ${(probability * 100).toFixed(1)}% probability of menopause. This is an estimate based on your age, symptoms, and health indicators. Please consult with a healthcare provider for confirmation and personalized care.`
          : `Based on your information, there is a ${(100 - probability * 100).toFixed(1)}% probability you are premenopausal. Continue monitoring your symptoms and consult a healthcare provider if you notice changes in your menstrual cycle or experience new symptoms.`
        }
      </Alert>

      {/* Diet Recommendations */}
      {hasRecommendations ? (
        <Card variant="outlined" sx={{ mb: 3 }}>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
              <RestaurantIcon color="primary" sx={{ fontSize: 32, mr: 1 }} />
              <Typography variant="h5" sx={{ fontWeight: 600 }}>
                Personalized Diet Recommendations
              </Typography>
            </Box>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
              Based on your symptoms and health profile, here are personalized dietary recommendations to help manage your health.
            </Typography>

            {/* Primary Recommendations */}
            {recommendations.primary && recommendations.primary.length > 0 && (
              <Accordion defaultExpanded sx={{ mb: 2 }}>
                <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                  <Typography variant="h6" sx={{ fontWeight: 600 }}>
                    Top Recommendations ({recommendations.primary.length})
                  </Typography>
                </AccordionSummary>
                <AccordionDetails>
                  <List>
                    {recommendations.primary.map((rec, idx) => (
                      <ListItem key={idx} sx={{ pl: 0 }}>
                        <ListItemIcon>
                          <LocalDiningIcon color="primary" />
                        </ListItemIcon>
                        <ListItemText
                          primary={
                            <Typography variant="body1" sx={{ fontWeight: 500 }}>
                              {rec.food}
                            </Typography>
                          }
                          secondary={
                            <Typography variant="body2" color="text.secondary">
                              {rec.reason || `Rich in ${rec.nutrient?.replace('_', ' ') || 'beneficial nutrients'}`}
                            </Typography>
                          }
                        />
                      </ListItem>
                    ))}
                  </List>
                </AccordionDetails>
              </Accordion>
            )}

            {/* Symptom-Specific Recommendations */}
            {recommendations.symptom_specific &&
              Object.keys(recommendations.symptom_specific).length > 0 && (
                <Box>
                  <Typography variant="h6" gutterBottom sx={{ fontWeight: 600, mb: 2 }}>
                    Recommendations by Symptom
                  </Typography>
                  {Object.entries(recommendations.symptom_specific).map(([symptom, recs]) => (
                    <Accordion key={symptom} sx={{ mb: 1 }}>
                      <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                        <Typography variant="subtitle1" sx={{ fontWeight: 600, textTransform: 'capitalize' }}>
                          {formatSymptomName(symptom)} ({recs.length} recommendations)
                        </Typography>
                      </AccordionSummary>
                      <AccordionDetails>
                        <List dense>
                          {recs.map((rec, idx) => (
                            <ListItem key={idx} sx={{ pl: 0 }}>
                              <ListItemIcon>
                                <LocalDiningIcon fontSize="small" color="primary" />
                              </ListItemIcon>
                              <ListItemText
                                primary={
                                  <Typography variant="body2" sx={{ fontWeight: 500 }}>
                                    {rec.food}
                                  </Typography>
                                }
                                secondary={
                                  <Typography variant="caption" color="text.secondary">
                                    {rec.reason || `Rich in ${rec.nutrient?.replace('_', ' ') || 'beneficial nutrients'}`}
                                  </Typography>
                                }
                              />
                            </ListItem>
                          ))}
                        </List>
                      </AccordionDetails>
                    </Accordion>
                  ))}
                </Box>
              )}

            {/* General Health Recommendations */}
            {recommendations.general_health && recommendations.general_health.length > 0 && (
              <Accordion sx={{ mt: 2 }}>
                <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                  <Typography variant="h6" sx={{ fontWeight: 600 }}>
                    General Health Recommendations ({recommendations.general_health.length})
                  </Typography>
                </AccordionSummary>
                <AccordionDetails>
                  <List>
                    {recommendations.general_health.map((rec, idx) => (
                      <ListItem key={idx} sx={{ pl: 0 }}>
                        <ListItemIcon>
                          <LocalDiningIcon color="primary" />
                        </ListItemIcon>
                        <ListItemText
                          primary={
                            <Typography variant="body1" sx={{ fontWeight: 500 }}>
                              {rec.food}
                            </Typography>
                          }
                          secondary={
                            <Typography variant="body2" color="text.secondary">
                              {rec.reason || `Rich in ${rec.nutrient?.replace('_', ' ') || 'beneficial nutrients'}`}
                            </Typography>
                          }
                        />
                      </ListItem>
                    ))}
                  </List>
                </AccordionDetails>
              </Accordion>
            )}
          </CardContent>
        </Card>
      ) : (
        <Card variant="outlined" sx={{ mb: 3 }}>
          <CardContent>
            <Alert severity="info">
              <Typography variant="body2">
                No specific dietary recommendations are needed at this time based on your current profile. 
                Maintain a balanced diet with plenty of fruits, vegetables, whole grains, and lean proteins.
              </Typography>
            </Alert>
          </CardContent>
        </Card>
      )}

      {/* Additional Information */}
      <Paper variant="outlined" sx={{ p: 2, bgcolor: 'grey.50' }}>
        <Typography variant="body2" color="text.secondary" align="center">
          <strong>Note:</strong> This prediction is for informational purposes only and should not replace professional medical advice. 
          Please consult with a healthcare provider for accurate diagnosis and personalized treatment.
        </Typography>
      </Paper>
    </Box>
  );
};

export default PredictionResult;
