"""E3-S1: ProteinModificationCircuit 테스트"""

import pytest
import numpy as np
from tccdp.circuits.protein_mod import (
    ProteinModificationCircuit,
    ProteinModificationExamples,
    create_protein_modification_circuit
)


class TestProteinModificationCircuit:
    """ProteinModificationCircuit 기본 테스트."""
    
    def test_initialization_default(self):
        """기본값으로 초기화."""
        circuit = ProteinModificationCircuit()
        assert circuit.name == "ProteinModificationCircuit"
        assert len(circuit.state_names) == 3
        assert circuit.state_names == ['U', 'P', 'Htot']
        assert len(circuit.params) == 6
    
    def test_initialization_with_params(self):
        """커스텀 파라미터로 초기화."""
        custom_params = {
            'k_kinase': 2.0,
            'k_pase': 1.0,
            'k_dU': 0.01,
            'k_dP': 0.01,
            'beta_H': 1.0,
            'k_dH': 0.02,
        }
        circuit = ProteinModificationCircuit(params=custom_params)
        assert circuit.params['k_kinase'] == 2.0
        assert circuit.params['k_pase'] == 1.0
    
    def test_get_initial_state(self):
        """초기 상태 반환."""
        circuit = ProteinModificationCircuit()
        initial_state = circuit.get_initial_state()
        assert len(initial_state) == 3
        assert initial_state[0] == 1.0  # U
        assert initial_state[1] == 0.0  # P
        assert initial_state[2] == 0.0  # Htot
    
    def test_get_derivatives(self):
        """미분값 계산."""
        circuit = ProteinModificationCircuit()
        y = np.array([1.0, 0.0, 0.0])
        derivatives = circuit.get_derivatives(t=0, y=y, stimulus=1.0)
        
        assert len(derivatives) == 3
        assert derivatives[0] < 0  # dU/dt should be negative
        assert derivatives[1] > 0  # dP/dt should be positive
    
    def test_get_output(self):
        """출력 계산."""
        circuit = ProteinModificationCircuit()
        y = np.array([1.0, 0.5, 0.1])
        output = circuit.get_output(y)
        assert output == 0.5  # P
    
    def test_get_propensities(self):
        """반응 율 계산."""
        circuit = ProteinModificationCircuit()
        y = np.array([1.0, 0.5, 0.1])
        propensities = circuit.get_propensities(y, stimulus=1.0)
        
        assert len(propensities) == 6
        assert np.all(propensities >= 0)
    
    def test_get_stoichiometry(self):
        """화학량론 행렬."""
        circuit = ProteinModificationCircuit()
        stoich = circuit.get_stoichiometry()
        
        assert len(stoich) == 6
        assert 'R1_phosphorylation' in stoich
        assert stoich['R1_phosphorylation'][0] == -1  # U
        assert stoich['R1_phosphorylation'][1] == 1   # P
    
    def test_validate_params(self):
        """파라미터 유효성."""
        circuit = ProteinModificationCircuit()
        assert circuit.validate_params()


class TestProteinModificationExamples:
    """예제 회로 팩토리 테스트."""
    
    def test_fast_kinase_response(self):
        """빠른 키나아제 응답."""
        circuit = ProteinModificationExamples.fast_kinase_response()
        assert circuit.params['k_kinase'] == 2.0
        assert circuit.params['k_pase'] == 0.1
        assert circuit.name == "FastKinaseResponse"
    
    def test_balanced_dynamics(self):
        """균형잡힌 동역학."""
        circuit = ProteinModificationExamples.balanced_dynamics()
        assert circuit.params['k_kinase'] == 1.0
        assert circuit.params['k_pase'] == 0.5
        assert circuit.name == "BalancedDynamics"
    
    def test_slow_phosphatase(self):
        """느린 포스파테이스."""
        circuit = ProteinModificationExamples.slow_phosphatase()
        assert circuit.params['k_kinase'] == 1.5
        assert circuit.params['k_pase'] == 0.05
        assert circuit.name == "SlowPhosphatase"


class TestProteinModificationFactory:
    """팩토리 함수 테스트."""
    
    def test_create_fast_circuit(self):
        """빠른 회로 생성."""
        circuit = create_protein_modification_circuit("fast")
        assert circuit.params['k_kinase'] == 2.0
    
    def test_create_balanced_circuit(self):
        """균형 회로 생성."""
        circuit = create_protein_modification_circuit("balanced")
        assert circuit.params['k_kinase'] == 1.0
    
    def test_create_slow_circuit(self):
        """느린 회로 생성."""
        circuit = create_protein_modification_circuit("slow")
        assert circuit.params['k_kinase'] == 1.5
    
    def test_invalid_circuit_type(self):
        """불명한 회로 타입."""
        with pytest.raises(ValueError):
            create_protein_modification_circuit("invalid")


class TestProteinModificationDynamics:
    """동역학 특성 테스트."""
    
    def test_stimulus_response(self):
        """자극에 따른 응답."""
        circuit = ProteinModificationCircuit()
        y = np.array([1.0, 0.0, 0.0])
        
        # 자극 없음
        deriv_no_stimulus = circuit.get_derivatives(t=0, y=y, stimulus=0.0)
        # 자극 있음
        deriv_with_stimulus = circuit.get_derivatives(t=0, y=y, stimulus=1.0)
        
        # P의 미분이 크게 달라야 함
        assert deriv_no_stimulus[1] < deriv_with_stimulus[1]
    
    def test_steady_state_approach(self):
        """정상 상태 접근."""
        circuit = ProteinModificationCircuit()
        y = circuit.get_initial_state()
        stimulus = 1.0
        
        # 여러 시간 스텝 시뮬레이션
        dt = 0.01
        for _ in range(1000):
            dy = circuit.get_derivatives(t=0, y=y, stimulus=stimulus)
            y = y + dy * dt
        
        # P가 증가해야 함
        assert y[1] > 0.1
        # U가 감소해야 함
        assert y[0] < 0.9


class TestProteinModificationIntegration:
    """통합 테스트."""
    
    def test_all_circuits_valid(self):
        """모든 예제 회로 유효성."""
        circuits = [
            ProteinModificationExamples.fast_kinase_response(),
            ProteinModificationExamples.balanced_dynamics(),
            ProteinModificationExamples.slow_phosphatase(),
        ]
        
        for circuit in circuits:
            assert circuit.validate_params()
            assert len(circuit.get_initial_state()) == 3
            assert len(circuit.get_stoichiometry()) == 6
    
    def test_all_required_methods(self):
        """모든 필수 메서드 구현 확인."""
        circuit = ProteinModificationCircuit()
        
        assert hasattr(circuit, 'get_default_params')
        assert hasattr(circuit, 'get_state_names')
        assert hasattr(circuit, 'get_initial_state')
        assert hasattr(circuit, 'get_derivatives')
        assert hasattr(circuit, 'get_output')
        assert hasattr(circuit, 'get_propensities')
        assert hasattr(circuit, 'get_stoichiometry')
