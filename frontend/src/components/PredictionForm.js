import React, { useState, useEffect } from 'react';
import {
  Paper,
  Grid,
  TextField,
  Button,
  Typography,
  Box,
  Card,
  CardContent,
  CircularProgress,
  Alert,
  Chip,
  Divider,
  Stepper,
  Step,
  StepLabel,
  FormControl,
  FormLabel,
  RadioGroup,
  FormControlLabel,
  Radio,
  Tooltip,
  IconButton,
} from '@mui/material';
import InfoIcon from '@mui/icons-material/Info';
import PredictionResult from './PredictionResult';
import { predictMenopause } from '../services/api';

const steps = ['Enter Information', 'Review & Submit', 'View Results'];

// Symptom severity options
const severityOptions = [
  { value: 0, label: 'None' },
  { value: 2, label: 'Mild' },
  { value: 5, label: 'Moderate' },
  { value: 7, label: 'Severe' },
  { value: 10, label: 'Very Severe' },
];

// Physical activity options
const activityOptions = [
  { value: 0, label: 'Sedentary (little/no exercise)' },
  { value: 3, label: 'Light (1-3 days/week)' },
  { value: 5, label: 'Moderate (3-5 days/week)' },
  { value: 7, label: 'Active (6-7 days/week)' },
  { value: 10, label: 'Very Active (intense daily exercise)' },
];

const PredictionForm = () => {
  const [activeStep, setActiveStep] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);

  const [formData, setFormData] = useState({
    age: '',
    bmi: '',
    weight: '',
    height: '',
    fsh: '',
    estradiol: '',
    hot_flashes: 0,
    sleep_disturbance: 0,
    mood_swings: 0,
    anxiety: 0,
    smoking: false,
    physical_activity: 0,
  });

  // Auto-calculate BMI when weight or height changes
  useEffect(() => {
    if (formData.weight && formData.height && !formData.bmi) {
      const weightKg = parseFloat(formData.weight);
      const heightCm = parseFloat(formData.height);
      if (weightKg > 0 && heightCm > 0) {
        const heightM = heightCm / 100;
        const calculatedBMI = (weightKg / (heightM * heightM)).toFixed(1);
        setFormData(prev => ({ ...prev, bmi: calculatedBMI }));
      }
    }
  }, [formData.weight, formData.height]);

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    const newValue = type === 'checkbox' ? checked : value;
    
    setFormData((prev) => {
      const updated = { ...prev, [name]: newValue };
      
      // Recalculate BMI if weight or height changes
      if ((name === 'weight' || name === 'height') && updated.weight && updated.height) {
        const weightKg = parseFloat(updated.weight);
        const heightCm = parseFloat(updated.height);
        if (weightKg > 0 && heightCm > 0) {
          const heightM = heightCm / 100;
          updated.bmi = (weightKg / (heightM * heightM)).toFixed(1);
        }
      }
      
      return updated;
    });
  };

  const handleNext = () => {
    setActiveStep((prev) => prev + 1);
  };

  const handleBack = () => {
    setActiveStep((prev) => prev - 1);
  };

  const handleSubmit = async () => {
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      // Convert form data to API format
      const apiData = {
        age: parseFloat(formData.age) || 0,
        bmi: formData.bmi ? parseFloat(formData.bmi) : null,
        weight: formData.weight ? parseFloat(formData.weight) : null,
        height: formData.height ? parseFloat(formData.height) : null,
        fsh: formData.fsh ? parseFloat(formData.fsh) : null,
        estradiol: formData.estradiol ? parseFloat(formData.estradiol) : null,
        hot_flashes: parseInt(formData.hot_flashes) || 0,
        sleep_disturbance: parseInt(formData.sleep_disturbance) || 0,
        mood_swings: parseInt(formData.mood_swings) || 0,
        anxiety: parseInt(formData.anxiety) || 0,
        smoking: formData.smoking,
        physical_activity: parseInt(formData.physical_activity) || 0,
      };

      const response = await predictMenopause(apiData);
      setResult(response.data);
      setActiveStep(2);
    } catch (err) {
      setError(err.message || 'An error occurred. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const renderFormStep = () => {
    if (activeStep === 0) {
      return (
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <Typography variant="h6" gutterBottom color="primary" sx={{ fontWeight: 600 }}>
              Basic Information
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
              Please provide your basic health information. All fields marked with * are required.
            </Typography>
          </Grid>
          
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              required
              label="Age"
              name="age"
              type="number"
              value={formData.age}
              onChange={handleChange}
              inputProps={{ min: 18, max: 100 }}
              helperText="Your current age in years"
            />
          </Grid>
          
          <Grid item xs={12} sm={6}>
            <FormControl component="fieldset">
              <FormLabel component="legend">Do you currently smoke?</FormLabel>
              <RadioGroup
                row
                name="smoking"
                value={formData.smoking.toString()}
                onChange={(e) => setFormData(prev => ({ ...prev, smoking: e.target.value === 'true' }))}
              >
                <FormControlLabel value="false" control={<Radio />} label="No" />
                <FormControlLabel value="true" control={<Radio />} label="Yes" />
              </RadioGroup>
            </FormControl>
          </Grid>

          <Grid item xs={12}>
            <Divider sx={{ my: 2 }} />
            <Typography variant="h6" gutterBottom color="primary" sx={{ fontWeight: 600 }}>
              Body Measurements
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
              Provide your weight and height. BMI will be calculated automatically.
            </Typography>
          </Grid>
          
          <Grid item xs={12} sm={4}>
            <TextField
              fullWidth
              label="Weight (kg)"
              name="weight"
              type="number"
              value={formData.weight}
              onChange={handleChange}
              inputProps={{ min: 30, max: 200, step: 0.1 }}
              helperText="Your weight in kilograms"
            />
          </Grid>
          
          <Grid item xs={12} sm={4}>
            <TextField
              fullWidth
              label="Height (cm)"
              name="height"
              type="number"
              value={formData.height}
              onChange={handleChange}
              inputProps={{ min: 100, max: 250, step: 0.1 }}
              helperText="Your height in centimeters"
            />
          </Grid>
          
          <Grid item xs={12} sm={4}>
            <TextField
              fullWidth
              label="BMI"
              name="bmi"
              type="number"
              value={formData.bmi}
              onChange={handleChange}
              inputProps={{ min: 10, max: 50, step: 0.1 }}
              helperText="Calculated automatically, or enter manually"
              disabled={!!(formData.weight && formData.height)}
            />
          </Grid>

          <Grid item xs={12}>
            <Divider sx={{ my: 2 }} />
            <Typography variant="h6" gutterBottom color="primary" sx={{ fontWeight: 600 }}>
              Hormone Levels (Optional)
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
              If you have recent lab results, you can enter them here. Leave blank if unknown.
            </Typography>
          </Grid>
          
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              label="FSH Level"
              name="fsh"
              type="number"
              value={formData.fsh}
              onChange={handleChange}
              inputProps={{ min: 0, step: 0.1 }}
              helperText="Follicle-Stimulating Hormone (from blood test)"
            />
          </Grid>
          
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              label="Estradiol Level"
              name="estradiol"
              type="number"
              value={formData.estradiol}
              onChange={handleChange}
              inputProps={{ min: 0, step: 0.1 }}
              helperText="Estradiol hormone level (from blood test)"
            />
          </Grid>

          <Grid item xs={12}>
            <Divider sx={{ my: 2 }} />
            <Typography variant="h6" gutterBottom color="primary" sx={{ fontWeight: 600 }}>
              Symptoms Assessment
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
              Please rate how much you experience each symptom. Be honest - this helps provide accurate predictions.
            </Typography>
          </Grid>
          
          <Grid item xs={12}>
            <FormControl component="fieldset" fullWidth>
              <FormLabel component="legend" sx={{ mb: 1 }}>
                Hot Flashes / Night Sweats
                <Tooltip title="Sudden feelings of heat, often with sweating, especially at night">
                  <IconButton size="small" sx={{ ml: 1 }}>
                    <InfoIcon fontSize="small" />
                  </IconButton>
                </Tooltip>
              </FormLabel>
              <RadioGroup
                row
                name="hot_flashes"
                value={formData.hot_flashes.toString()}
                onChange={handleChange}
              >
                {severityOptions.map((option) => (
                  <FormControlLabel
                    key={option.value}
                    value={option.value.toString()}
                    control={<Radio />}
                    label={option.label}
                  />
                ))}
              </RadioGroup>
            </FormControl>
          </Grid>

          <Grid item xs={12}>
            <FormControl component="fieldset" fullWidth>
              <FormLabel component="legend" sx={{ mb: 1 }}>
                Sleep Disturbances
                <Tooltip title="Difficulty falling asleep, staying asleep, or waking up frequently">
                  <IconButton size="small" sx={{ ml: 1 }}>
                    <InfoIcon fontSize="small" />
                  </IconButton>
                </Tooltip>
              </FormLabel>
              <RadioGroup
                row
                name="sleep_disturbance"
                value={formData.sleep_disturbance.toString()}
                onChange={handleChange}
              >
                {severityOptions.map((option) => (
                  <FormControlLabel
                    key={option.value}
                    value={option.value.toString()}
                    control={<Radio />}
                    label={option.label}
                  />
                ))}
              </RadioGroup>
            </FormControl>
          </Grid>

          <Grid item xs={12}>
            <FormControl component="fieldset" fullWidth>
              <FormLabel component="legend" sx={{ mb: 1 }}>
                Mood Swings
                <Tooltip title="Rapid changes in mood, irritability, or emotional sensitivity">
                  <IconButton size="small" sx={{ ml: 1 }}>
                    <InfoIcon fontSize="small" />
                  </IconButton>
                </Tooltip>
              </FormLabel>
              <RadioGroup
                row
                name="mood_swings"
                value={formData.mood_swings.toString()}
                onChange={handleChange}
              >
                {severityOptions.map((option) => (
                  <FormControlLabel
                    key={option.value}
                    value={option.value.toString()}
                    control={<Radio />}
                    label={option.label}
                  />
                ))}
              </RadioGroup>
            </FormControl>
          </Grid>

          <Grid item xs={12}>
            <FormControl component="fieldset" fullWidth>
              <FormLabel component="legend" sx={{ mb: 1 }}>
                Anxiety
                <Tooltip title="Feelings of worry, nervousness, or unease">
                  <IconButton size="small" sx={{ ml: 1 }}>
                    <InfoIcon fontSize="small" />
                  </IconButton>
                </Tooltip>
              </FormLabel>
              <RadioGroup
                row
                name="anxiety"
                value={formData.anxiety.toString()}
                onChange={handleChange}
              >
                {severityOptions.map((option) => (
                  <FormControlLabel
                    key={option.value}
                    value={option.value.toString()}
                    control={<Radio />}
                    label={option.label}
                  />
                ))}
              </RadioGroup>
            </FormControl>
          </Grid>

          <Grid item xs={12}>
            <Divider sx={{ my: 2 }} />
            <Typography variant="h6" gutterBottom color="primary" sx={{ fontWeight: 600 }}>
              Lifestyle
            </Typography>
          </Grid>
          
          <Grid item xs={12}>
            <FormControl component="fieldset" fullWidth>
              <FormLabel component="legend" sx={{ mb: 1 }}>
                Physical Activity Level
                <Tooltip title="How often do you engage in physical exercise or activities?">
                  <IconButton size="small" sx={{ ml: 1 }}>
                    <InfoIcon fontSize="small" />
                  </IconButton>
                </Tooltip>
              </FormLabel>
              <RadioGroup
                name="physical_activity"
                value={formData.physical_activity.toString()}
                onChange={handleChange}
              >
                {activityOptions.map((option) => (
                  <FormControlLabel
                    key={option.value}
                    value={option.value.toString()}
                    control={<Radio />}
                    label={option.label}
                  />
                ))}
              </RadioGroup>
            </FormControl>
          </Grid>
        </Grid>
      );
    } else if (activeStep === 1) {
      return (
        <Box>
          <Typography variant="h6" gutterBottom color="primary" sx={{ fontWeight: 600 }}>
            Review Your Information
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            Please review your information before submitting. You can go back to make changes.
          </Typography>
          <Card variant="outlined" sx={{ mt: 2 }}>
            <CardContent>
              <Typography variant="body2" component="div" sx={{ mb: 1 }}>
                <strong>Age:</strong> {formData.age} years
              </Typography>
              {formData.bmi && (
                <Typography variant="body2" component="div" sx={{ mb: 1 }}>
                  <strong>BMI:</strong> {formData.bmi}
                </Typography>
              )}
              {formData.weight && formData.height && (
                <Typography variant="body2" component="div" sx={{ mb: 1 }}>
                  <strong>Weight:</strong> {formData.weight} kg, <strong>Height:</strong> {formData.height} cm
                </Typography>
              )}
              {formData.fsh && (
                <Typography variant="body2" component="div" sx={{ mb: 1 }}>
                  <strong>FSH:</strong> {formData.fsh}
                </Typography>
              )}
              <Typography variant="body2" component="div" sx={{ mb: 1 }}>
                <strong>Smoking:</strong> {formData.smoking ? 'Yes' : 'No'}
              </Typography>
              <Typography variant="body2" component="div" sx={{ mb: 1 }}>
                <strong>Hot Flashes:</strong> {severityOptions.find(o => o.value === parseInt(formData.hot_flashes))?.label || 'None'}
              </Typography>
              <Typography variant="body2" component="div" sx={{ mb: 1 }}>
                <strong>Sleep Disturbance:</strong> {severityOptions.find(o => o.value === parseInt(formData.sleep_disturbance))?.label || 'None'}
              </Typography>
              <Typography variant="body2" component="div" sx={{ mb: 1 }}>
                <strong>Mood Swings:</strong> {severityOptions.find(o => o.value === parseInt(formData.mood_swings))?.label || 'None'}
              </Typography>
              <Typography variant="body2" component="div" sx={{ mb: 1 }}>
                <strong>Anxiety:</strong> {severityOptions.find(o => o.value === parseInt(formData.anxiety))?.label || 'None'}
              </Typography>
              <Typography variant="body2" component="div">
                <strong>Physical Activity:</strong> {activityOptions.find(o => o.value === parseInt(formData.physical_activity))?.label || 'Not specified'}
              </Typography>
            </CardContent>
          </Card>
        </Box>
      );
    }
    return null;
  };

  return (
    <Box>
      <Paper sx={{ p: 4, mb: 3 }} elevation={3}>
        <Stepper activeStep={activeStep} sx={{ mb: 4 }}>
          {steps.map((label) => (
            <Step key={label}>
              <StepLabel>{label}</StepLabel>
            </Step>
          ))}
        </Stepper>

        {error && (
          <Alert severity="error" sx={{ mb: 3 }}>
            {error}
          </Alert>
        )}

        {renderFormStep()}

        {activeStep === 2 && result && (
          <PredictionResult result={result} />
        )}

        <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 4 }}>
          <Button
            disabled={activeStep === 0}
            onClick={handleBack}
          >
            Back
          </Button>
          {activeStep < steps.length - 1 ? (
            <Button
              variant="contained"
              onClick={activeStep === 0 ? handleNext : handleSubmit}
              disabled={loading || !formData.age}
              sx={{ mt: 2, py: 1.5 }}
            >
              {loading ? <CircularProgress size={24} /> : activeStep === 0 ? 'Next' : 'Submit'}
            </Button>
          ) : (
            <Button
              variant="contained"
              onClick={() => {
                setActiveStep(0);
                setResult(null);
                setError(null);
              }}
            >
              New Prediction
            </Button>
          )}
        </Box>
      </Paper>
    </Box>
  );
};

export default PredictionForm;
