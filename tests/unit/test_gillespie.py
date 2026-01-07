"""E3-S2: Gillespie Stochastic Simulator 테스트"""

import pytest
import numpy as np
from tccdp.simulators.gillespie import GillespieSimulator, CircuitGillespieAdapter
from tccdp.circuits.protein_mod import ProteinModificationCircuit


class SimpleDegradationCircuit:
    """테스트용 간단한 분해 회로: A → ∅"""
    
    def get_stoichiometry(self):
        return {
            'degradation': np.array([-1])
        }
    
    def get_propensities(self, y, stimulus=0.0):
        return np.array([0.5 * y[0]])  # First-order degradation


class SimpleProductionCircuit:
    """테스트용 간단한 생산 회로: ∅ → A"""
    
    def get_stoichiometry(self):
        return {
            'production': np.array([1])
        }
    
    def get_propensities(self, y, stimulus=0.0):
        return np.array([1.0])  # Constant production


class TestGillespieSimulator:
    """Gillespie 시뮬레이터 기본 테스트."""
    
    def test_initialization(self):
        """시뮬레이터 초기화."""
        circuit = SimpleDegradationCircuit()
        simulator = GillespieSimulator(
            get_propensities=circuit.get_propensities,
            stoichiometry=circuit.get_stoichiometry(),
            num_species=1
        )
        assert simulator.num_species == 1
        assert len(simulator.stoichiometry) == 1
    
    def test_simple_degradation(self):
        """간단한 분해 시뮬레이션."""
        circuit = SimpleDegradationCircuit()
        simulator = GillespieSimulator(
            get_propensities=circuit.get_propensities,
            stoichiometry=circuit.get_stoichiometry(),
            num_species=1
        )
        
        state = np.array([10.0])
        t_span = (0, 10)
        result = simulator.simulate(state, t_span, n_points=100, seed=42)
        
        assert 't' in result
        assert 'y' in result
        assert 'events' in result
        assert 'success' in result
        assert result['success']
        assert result['y'].shape[1] <= 100
        # 분해가 일어나므로 상태값이 감소해야 함
        assert result['y'][0, -1] < result['y'][0, 0]
    
    def test_result_dimensions(self):
        """결과 차원 확인."""
        circuit = SimpleDegradationCircuit()
        simulator = GillespieSimulator(
            get_propensities=circuit.get_propensities,
            stoichiometry=circuit.get_stoichiometry(),
            num_species=1
        )
        
        state = np.array([10.0])
        result = simulator.simulate(state, (0, 5), n_points=50)
        
        assert result['y'].shape[0] == 1  # num_species
        assert len(result['t']) == result['y'].shape[1]
    
    def test_reproducibility_with_seed(self):
        """시드 재현성."""
        circuit = SimpleDegradationCircuit()
        simulator = GillespieSimulator(
            get_propensities=circuit.get_propensities,
            stoichiometry=circuit.get_stoichiometry(),
            num_species=1
        )
        
        state = np.array([10.0])
        
        # 같은 시드로 두 번 시뮬레이션
        result1 = simulator.simulate(state, (0, 5), seed=123)
        result2 = simulator.simulate(state, (0, 5), seed=123)
        
        np.testing.assert_array_almost_equal(result1['t'], result2['t'])
        np.testing.assert_array_almost_equal(result1['y'], result2['y'])
    
    def test_different_seeds_different_results(self):
        """다른 시드로 다른 결과."""
        circuit = SimpleDegradationCircuit()
        simulator = GillespieSimulator(
            get_propensities=circuit.get_propensities,
            stoichiometry=circuit.get_stoichiometry(),
            num_species=1
        )
        
        state = np.array([10.0])
        
        result1 = simulator.simulate(state, (0, 5), seed=123)
        result2 = simulator.simulate(state, (0, 5), seed=456)
        
        # 적어도 일부는 달라야 함 (매우 낮은 확률로 우연히 같을 수 있음)
        assert not np.allclose(result1['y'], result2['y'])


class TestGillespieEnsemble:
    """앙상블 시뮬레이션 테스트."""
    
    def test_ensemble_dimensions(self):
        """앙상블 차원 확인."""
        circuit = SimpleDegradationCircuit()
        simulator = GillespieSimulator(
            get_propensities=circuit.get_propensities,
            stoichiometry=circuit.get_stoichiometry(),
            num_species=1
        )
        
        state = np.array([10.0])
        result = simulator.simulate_ensemble(
            state, (0, 5), num_trajectories=10, n_points=50, seed=42
        )
        
        assert 'trajectories' in result
        assert result['trajectories'].shape[0] == 10  # num_trajectories
        assert result['trajectories'].shape[1] == 1   # num_species
    
    def test_ensemble_statistics(self):
        """앙상블 통계."""
        circuit = SimpleDegradationCircuit()
        simulator = GillespieSimulator(
            get_propensities=circuit.get_propensities,
            stoichiometry=circuit.get_stoichiometry(),
            num_species=1
        )
        
        state = np.array([10.0])
        result = simulator.simulate_ensemble(
            state, (0, 5), num_trajectories=20, seed=42
        )
        
        assert 'mean' in result
        assert 'std' in result
        assert result['mean'].shape[0] == 1
        assert result['std'].shape[0] == 1
    
    def test_ensemble_mean_degradation(self):
        """앙상블 평균이 감소."""
        circuit = SimpleDegradationCircuit()
        simulator = GillespieSimulator(
            get_propensities=circuit.get_propensities,
            stoichiometry=circuit.get_stoichiometry(),
            num_species=1
        )
        
        state = np.array([10.0])
        result = simulator.simulate_ensemble(
            state, (0, 5), num_trajectories=30, seed=42
        )
        
        # 분해가 일어나므로 평균도 감소해야 함
        assert result['mean'][0, -1] < result['mean'][0, 0]


class TestCircuitGillespieAdapter:
    """CircuitGillespieAdapter 테스트."""
    
    def test_create_adapter(self):
        """어댑터 생성."""
        circuit = ProteinModificationCircuit()
        simulator = CircuitGillespieAdapter.create_simulator(circuit)
        
        assert simulator is not None
        assert simulator.num_species == 3
    
    def test_adapter_simulate(self):
        """어댑터 시뮬레이션."""
        circuit = ProteinModificationCircuit()
        
        result = CircuitGillespieAdapter.simulate(
            circuit, (0, 5), stimulus=1.0, seed=42
        )
        
        assert 't' in result
        assert 'y' in result
        assert result['success']
    
    def test_adapter_ensemble(self):
        """어댑터 앙상블."""
        circuit = ProteinModificationCircuit()
        
        result = CircuitGillespieAdapter.simulate_ensemble(
            circuit, (0, 5), num_trajectories=10, seed=42
        )
        
        assert 'trajectories' in result
        assert result['trajectories'].shape[0] == 10


class TestGillespieProteinModificationCircuit:
    """ProteinModificationCircuit와의 통합 테스트."""
    
    def test_protein_mod_simulation(self):
        """단백질 수정 회로 시뮬레이션."""
        circuit = ProteinModificationCircuit()
        state = circuit.get_initial_state()
        
        simulator = GillespieSimulator(
            get_propensities=circuit.get_propensities,
            stoichiometry=circuit.get_stoichiometry(),
            num_species=3
        )
        
        result = simulator.simulate(state, (0, 5), stimulus=1.0, seed=42)
        
        assert result['success']
        assert result['y'].shape[0] == 3
        # 여러 시뮬레이션이므로 P가 반드시 증가하지는 않음
        # 하지만 시뮬레이션이 수행되고 reasonable한 범위의 값을 가져야 함
        assert result['y'][1, -1] >= 0  # P >= 0
        assert result['y'][1, -1] <= 1.0  # P <= 1.0
    
    def test_protein_mod_ensemble(self):
        """단백질 수정 회로 앙상블."""
        circuit = ProteinModificationCircuit()
        state = circuit.get_initial_state()
        
        simulator = GillespieSimulator(
            get_propensities=circuit.get_propensities,
            stoichiometry=circuit.get_stoichiometry(),
            num_species=3
        )
        
        result = simulator.simulate_ensemble(
            state, (0, 5), num_trajectories=10, seed=42
        )
        
        assert result['trajectories'].shape[0] == 10
        assert result['mean'].shape[0] == 3


class TestGillespieEdgeCases:
    """경계 케이스 테스트."""
    
    def test_zero_propensity(self):
        """영 반응율."""
        circuit = SimpleDegradationCircuit()
        simulator = GillespieSimulator(
            get_propensities=circuit.get_propensities,
            stoichiometry=circuit.get_stoichiometry(),
            num_species=1
        )
        
        state = np.array([0.0])  # Empty state
        result = simulator.simulate(state, (0, 5))
        
        assert result['success']
        assert result['y'][0, -1] == 0.0
    
    def test_large_propensity(self):
        """큰 반응율."""
        circuit = SimpleDegradationCircuit()
        simulator = GillespieSimulator(
            get_propensities=circuit.get_propensities,
            stoichiometry=circuit.get_stoichiometry(),
            num_species=1
        )
        
        state = np.array([1000.0])
        result = simulator.simulate(state, (0, 5), seed=42)
        
        assert result['success']
        assert result['events'] > 0
    
    def test_short_time_span(self):
        """짧은 시간 범위."""
        circuit = SimpleDegradationCircuit()
        simulator = GillespieSimulator(
            get_propensities=circuit.get_propensities,
            stoichiometry=circuit.get_stoichiometry(),
            num_species=1
        )
        
        state = np.array([10.0])
        result = simulator.simulate(state, (0, 0.1), seed=42)
        
        assert result['success']


class TestGillespiePerformance:
    """성능 테스트."""
    
    def test_performance_small_system(self):
        """작은 시스템 성능."""
        circuit = SimpleDegradationCircuit()
        simulator = GillespieSimulator(
            get_propensities=circuit.get_propensities,
            stoichiometry=circuit.get_stoichiometry(),
            num_species=1
        )
        
        import time
        state = np.array([100.0])
        
        start_time = time.time()
        result = simulator.simulate(state, (0, 10), seed=42)
        elapsed = time.time() - start_time
        
        # 작은 시스템은 1초 이내에 완료되어야 함
        assert elapsed < 1.0
        assert result['success']
    
    def test_ensemble_performance(self):
        """앙상블 성능."""
        circuit = SimpleDegradationCircuit()
        simulator = GillespieSimulator(
            get_propensities=circuit.get_propensities,
            stoichiometry=circuit.get_stoichiometry(),
            num_species=1
        )
        
        import time
        state = np.array([50.0])
        
        start_time = time.time()
        result = simulator.simulate_ensemble(
            state, (0, 5), num_trajectories=10, seed=42
        )
        elapsed = time.time() - start_time
        
        # 앙상블은 10초 이내에 완료되어야 함
        assert elapsed < 10.0
        assert result['trajectories'].shape[0] == 10
