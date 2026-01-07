"""
ProteinModificationCircuit: 단백질 인산화/탈인산화 기반 회로
"""

from typing import Dict, Optional
import numpy as np
from numpy.typing import NDArray
import logging

from tccdp.core.base_circuit import BaseCircuit

logger = logging.getLogger(__name__)


class ProteinModificationCircuit(BaseCircuit):
    """단백질 인산화/탈인산화 기반 신호 전달 회로."""
    
    def __init__(
        self,
        params: Optional[Dict[str, float]] = None,
        name: str = "ProteinModificationCircuit"
    ):
        """
        ProteinModificationCircuit 초기화.
        
        Args:
            params: 파라미터 딕셔너리
            name: 회로 이름
        """
        super().__init__(params=params)
        self.name = name
    
    def get_default_params(self) -> Dict[str, float]:
        """기본 파라미터값."""
        return {
            'k_kinase': 1.0,
            'k_pase': 0.5,
            'k_dU': 0.01,
            'k_dP': 0.01,
            'beta_H': 1.0,
            'k_dH': 0.02,
        }
    
    def get_state_names(self) -> list:
        """상태 변수 이름."""
        return ['U', 'P', 'Htot']
    
    def get_initial_state(self) -> NDArray[np.float64]:
        """초기 상태: [U=1.0, P=0.0, Htot=0.0]."""
        return np.array([1.0, 0.0, 0.0], dtype=np.float64)
    
    def get_derivatives(
        self,
        t: float,
        y: NDArray[np.float64],
        stimulus: float = 0.0
    ) -> NDArray[np.float64]:
        """상태의 미분값 (ODE 시스템)."""
        U, P, Htot = y
        k_kinase = self.params.get('k_kinase', 1.0)
        k_pase = self.params.get('k_pase', 0.5)
        k_dU = self.params.get('k_dU', 0.01)
        k_dP = self.params.get('k_dP', 0.01)
        beta_H = self.params.get('beta_H', 1.0)
        k_dH = self.params.get('k_dH', 0.02)
        
        dU_dt = -k_kinase * U * stimulus + k_pase * P - k_dU * U
        dP_dt = k_kinase * U * stimulus - k_pase * P - k_dP * P
        dHtot_dt = beta_H * P - k_dH * Htot
        
        return np.array([dU_dt, dP_dt, dHtot_dt])
    
    def get_output(self, y: NDArray[np.float64]) -> float:
        """출력: P (인산화된 단백질)."""
        return float(y[1])  # P is the second state
    
    def get_stoichiometry(self) -> Dict[str, NDArray[np.int64]]:
        """확률적 시뮬레이션용 화학량론 행렬."""
        return {
            'R1_phosphorylation': np.array([-1, 1, 0]),
            'R2_dephosphorylation': np.array([1, -1, 0]),
            'R3_U_degradation': np.array([-1, 0, 0]),
            'R4_P_degradation': np.array([0, -1, 0]),
            'R5_H_production': np.array([0, 0, 1]),
            'R6_H_degradation': np.array([0, 0, -1]),
        }
    
    def get_propensities(self, y: NDArray[np.float64], stimulus: float = 0.0) -> NDArray[np.float64]:
        """확률적 시뮬레이션용 반응 율."""
        U, P, Htot = y
        k_kinase = self.params.get('k_kinase', 1.0)
        k_pase = self.params.get('k_pase', 0.5)
        k_dU = self.params.get('k_dU', 0.01)
        k_dP = self.params.get('k_dP', 0.01)
        beta_H = self.params.get('beta_H', 1.0)
        k_dH = self.params.get('k_dH', 0.02)
        
        return np.array([
            k_kinase * U * stimulus,  # R1: phosphorylation
            k_pase * P,               # R2: dephosphorylation
            k_dU * U,                 # R3: U degradation
            k_dP * P,                 # R4: P degradation
            beta_H * P,               # R5: H production
            k_dH * Htot,              # R6: H degradation
        ])
    
    def validate_params(self) -> bool:
        """파라미터 유효성 검사."""
        required_keys = {'k_kinase', 'k_pase', 'k_dU', 'k_dP', 'beta_H', 'k_dH'}
        if not required_keys.issubset(self.params.keys()):
            return False
        
        for key, value in self.params.items():
            if not isinstance(value, (int, float)) or value < 0:
                return False
        
        return True


class ProteinModificationExamples:
    """ProteinModificationCircuit 예제 팩토리."""
    
    @staticmethod
    def fast_kinase_response() -> ProteinModificationCircuit:
        """빠른 키나아제 응답 (고 k_kinase, 저 k_pase)."""
        params = {
            'k_kinase': 2.0,
            'k_pase': 0.1,
            'k_dU': 0.01,
            'k_dP': 0.01,
            'beta_H': 1.0,
            'k_dH': 0.02,
        }
        return ProteinModificationCircuit(params, "FastKinaseResponse")
    
    @staticmethod
    def balanced_dynamics() -> ProteinModificationCircuit:
        """균형잡힌 동역학 (중간 속도)."""
        params = {
            'k_kinase': 1.0,
            'k_pase': 0.5,
            'k_dU': 0.01,
            'k_dP': 0.01,
            'beta_H': 1.0,
            'k_dH': 0.02,
        }
        return ProteinModificationCircuit(params, "BalancedDynamics")
    
    @staticmethod
    def slow_phosphatase() -> ProteinModificationCircuit:
        """느린 포스파테이스 (고 k_kinase, 저 k_pase)."""
        params = {
            'k_kinase': 1.5,
            'k_pase': 0.05,
            'k_dU': 0.01,
            'k_dP': 0.01,
            'beta_H': 1.0,
            'k_dH': 0.02,
        }
        return ProteinModificationCircuit(params, "SlowPhosphatase")


def create_protein_modification_circuit(
    circuit_type: str = "balanced"
) -> ProteinModificationCircuit:
    """
    파라미터로 ProteinModificationCircuit 생성.
    
    Args:
        circuit_type: "fast", "balanced", "slow"
    
    Returns:
        ProteinModificationCircuit
    
    Raises:
        ValueError: 불명의 회로 타입
    """
    if circuit_type == "fast":
        return ProteinModificationExamples.fast_kinase_response()
    elif circuit_type == "balanced":
        return ProteinModificationExamples.balanced_dynamics()
    elif circuit_type == "slow":
        return ProteinModificationExamples.slow_phosphatase()
    else:
        raise ValueError(f"Unknown circuit type: {circuit_type}")
