"""
Analyzes training metrics for patterns, health, and recommendations
"""
import numpy as np
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum


class TrainingStatus(Enum):
    """Training status indicators"""
    NOT_STARTED = "Not Started"
    WARMING_UP = "Warming Up"
    HEALTHY = "Healthy Learning"
    PLATEAU = "Plateau Detected"
    OVERFITTING = "Overfitting Risk"
    DIVERGING = "Diverging"
    UNSTABLE = "Unstable"
    COMPLETED = "Completed"


class HealthStatus(Enum):
    """Health status for color coding"""
    GOOD = "good"
    WARNING = "warning"
    CRITICAL = "critical"
    NEUTRAL = "neutral"


class MetricsAnalyzer:
    """Analyzes training metrics for patterns and provides recommendations"""

    def __init__(self):
        """Initialize analyzer with thresholds"""
        # Thresholds for pattern detection
        self.overfit_threshold = 0.02
        self.plateau_threshold_steps = 500
        self.plateau_threshold_variance = 0.001
        self.divergence_threshold = 2.0
        self.high_variance_threshold = 0.5
        self.warmup_steps = 100

        # Window sizes for analysis
        self.short_window = 50
        self.medium_window = 100
        self.long_window = 500

    def analyze(self, loss_history: List[float],
                lr_history: Optional[List[float]] = None,
                steps: Optional[List[int]] = None) -> Dict[str, Any]:
        """
        Comprehensive analysis of training metrics

        Args:
            loss_history: List of loss values
            lr_history: Optional list of learning rates
            steps: Optional list of step numbers

        Returns:
            Dictionary with analysis results
        """
        if not loss_history or len(loss_history) < 10:
            return self._initial_state()

        # Convert to numpy arrays
        losses = np.array(loss_history)

        # Get current metrics
        current_loss = losses[-1]
        num_points = len(losses)

        # Compute statistics
        stats = self._compute_statistics(losses)

        # Detect patterns
        status = self._detect_status(losses, stats)
        health = self._determine_health(status, stats)

        # Generate recommendation
        recommendation = self._generate_recommendation(status, stats, lr_history)

        # Calculate trend
        trend = self._calculate_trend(losses)

        # Estimate time to completion if steps provided
        eta = self._estimate_completion_time(steps, losses) if steps else None

        return {
            'status': status.value,
            'health': health.value,
            'recommendation': recommendation,
            'statistics': stats,
            'trend': trend,
            'eta': eta,
            'current_loss': current_loss,
            'num_points': num_points,
        }

    def _initial_state(self) -> Dict[str, Any]:
        """Return initial state when not enough data"""
        return {
            'status': TrainingStatus.NOT_STARTED.value,
            'health': HealthStatus.NEUTRAL.value,
            'recommendation': "Gathering data...",
            'statistics': {},
            'trend': None,
            'eta': None,
            'current_loss': None,
            'num_points': 0,
        }

    def _compute_statistics(self, losses: np.ndarray) -> Dict[str, float]:
        """Compute statistical metrics"""
        stats = {
            'mean': np.mean(losses),
            'std': np.std(losses),
            'min': np.min(losses),
            'max': np.max(losses),
            'median': np.median(losses),
        }

        # Variance ratio (coefficient of variation)
        if stats['mean'] > 0:
            stats['variance_ratio'] = stats['std'] / stats['mean']
        else:
            stats['variance_ratio'] = 0

        # Recent statistics (last 10% of data)
        recent_window = max(10, len(losses) // 10)
        recent_losses = losses[-recent_window:]
        stats['recent_mean'] = np.mean(recent_losses)
        stats['recent_std'] = np.std(recent_losses)

        # Compute trend slope
        if len(losses) >= 20:
            x = np.arange(len(losses))
            slope, intercept = np.polyfit(x, losses, 1)
            stats['slope'] = slope
            stats['intercept'] = intercept
        else:
            stats['slope'] = 0
            stats['intercept'] = stats['mean']

        return stats

    def _detect_status(self, losses: np.ndarray, stats: Dict[str, float]) -> TrainingStatus:
        """Detect training status based on patterns"""
        num_points = len(losses)

        # Check if still warming up
        if num_points < self.warmup_steps:
            return TrainingStatus.WARMING_UP

        # Check for overfitting (very low loss)
        if stats['recent_mean'] < self.overfit_threshold:
            return TrainingStatus.OVERFITTING

        # Check for plateau
        if num_points >= self.plateau_threshold_steps:
            recent_window = min(self.plateau_threshold_steps, len(losses) // 2)
            recent_losses = losses[-recent_window:]
            if np.std(recent_losses) < self.plateau_threshold_variance:
                return TrainingStatus.PLATEAU

        # Check for divergence (increasing loss)
        if stats['slope'] > 0 and stats['recent_mean'] > stats['mean'] * self.divergence_threshold:
            return TrainingStatus.DIVERGING

        # Check for instability (high variance)
        if stats['variance_ratio'] > self.high_variance_threshold:
            return TrainingStatus.UNSTABLE

        # Otherwise, healthy learning
        return TrainingStatus.HEALTHY

    def _determine_health(self, status: TrainingStatus, stats: Dict[str, float]) -> HealthStatus:
        """Determine health status for UI color coding"""
        if status in [TrainingStatus.HEALTHY, TrainingStatus.WARMING_UP]:
            return HealthStatus.GOOD
        elif status == TrainingStatus.NOT_STARTED:
            return HealthStatus.NEUTRAL
        elif status in [TrainingStatus.PLATEAU, TrainingStatus.OVERFITTING, TrainingStatus.UNSTABLE]:
            return HealthStatus.WARNING
        else:  # DIVERGING
            return HealthStatus.CRITICAL

    def _generate_recommendation(self, status: TrainingStatus,
                                stats: Dict[str, float],
                                lr_history: Optional[List[float]] = None) -> str:
        """Generate actionable recommendations"""
        if status == TrainingStatus.NOT_STARTED:
            return "Waiting for training to begin..."

        elif status == TrainingStatus.WARMING_UP:
            return f"Model is warming up, {self.warmup_steps - len(stats)} steps until full analysis"

        elif status == TrainingStatus.HEALTHY:
            if stats['slope'] < -1e-5:
                return "Training is progressing well, loss decreasing steadily"
            else:
                return "Training is stable, monitor for convergence"

        elif status == TrainingStatus.OVERFITTING:
            return f"Loss very low ({stats['recent_mean']:.4f}), consider stopping to prevent overfitting"

        elif status == TrainingStatus.PLATEAU:
            if lr_history and len(lr_history) > 0:
                current_lr = lr_history[-1]
                return f"Learning has plateaued, consider reducing LR (current: {current_lr:.2e})"
            else:
                return "Learning has plateaued, consider reducing learning rate or stopping"

        elif status == TrainingStatus.DIVERGING:
            return "Loss is increasing! Check learning rate and batch size"

        elif status == TrainingStatus.UNSTABLE:
            return "High loss variance detected, consider reducing learning rate"

        else:
            return "Training completed"

    def _calculate_trend(self, losses: np.ndarray) -> Dict[str, Any]:
        """Calculate trend information"""
        if len(losses) < 20:
            return {'direction': 'unknown', 'strength': 0}

        # Linear regression for trend
        x = np.arange(len(losses))
        slope, _ = np.polyfit(x, losses, 1)

        # Determine direction and strength
        if abs(slope) < 1e-6:
            direction = 'stable'
        elif slope < 0:
            direction = 'decreasing'
        else:
            direction = 'increasing'

        # Normalize slope for strength (0-1 scale)
        max_expected_slope = 0.01  # Adjust based on typical values
        strength = min(abs(slope) / max_expected_slope, 1.0)

        return {
            'direction': direction,
            'strength': strength,
            'slope': slope,
        }

    def _estimate_completion_time(self, steps: List[int], losses: np.ndarray) -> Optional[Dict[str, Any]]:
        """Estimate time to completion based on convergence rate"""
        if len(steps) < 100 or len(losses) < 100:
            return None

        # Calculate convergence rate
        recent_losses = losses[-100:]
        if np.std(recent_losses) < self.plateau_threshold_variance:
            # Already converged
            return {'status': 'converged', 'steps_remaining': 0}

        # Estimate based on loss reduction rate
        slope, _ = np.polyfit(np.arange(len(recent_losses)), recent_losses, 1)

        if slope >= 0:
            # Not converging
            return {'status': 'not_converging', 'steps_remaining': None}

        # Estimate steps to reach threshold
        current_loss = losses[-1]
        target_loss = self.overfit_threshold * 2  # Conservative target

        if current_loss <= target_loss:
            return {'status': 'reached_target', 'steps_remaining': 0}

        # Linear extrapolation (simplified)
        steps_per_loss_unit = 1 / abs(slope)
        loss_to_reduce = current_loss - target_loss
        estimated_steps = int(loss_to_reduce * steps_per_loss_unit)

        return {
            'status': 'converging',
            'steps_remaining': estimated_steps,
            'target_loss': target_loss,
            'current_loss': current_loss,
        }

    def detect_anomalies(self, losses: List[float], sensitivity: float = 3.0) -> List[int]:
        """
        Detect anomalous loss values

        Args:
            losses: List of loss values
            sensitivity: Number of standard deviations for anomaly threshold

        Returns:
            List of indices where anomalies were detected
        """
        if len(losses) < 10:
            return []

        losses_array = np.array(losses)
        mean = np.mean(losses_array)
        std = np.std(losses_array)

        # Find values outside sensitivity * std
        threshold_upper = mean + (sensitivity * std)
        threshold_lower = mean - (sensitivity * std)

        anomalies = []
        for i, loss in enumerate(losses_array):
            if loss > threshold_upper or loss < threshold_lower:
                anomalies.append(i)

        return anomalies