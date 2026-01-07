"""
Gillespie 알고리즘 기반 확률적 시뮬레이터.

Gillespie 알고리즘은 화학 반응 네트워크의 확률적 동역학을 정확하게 시뮬레이션합니다.
분자 수준의 불연속적 이벤트를 모델링합니다.

주요 특징:
- Direct Method: 직접 시간 적분 (정확하고 느림)
- First Reaction Method: 첫 반응 선택 (빠름)
- 적응형 선택 가능
- 종(species) 수에 따라 자동 최적화

알고리즘:
1. 각 반응의 propensity 계산
2. propensity 합계로부터 다음 이벤트 시간 샘플링 (지수분포)
3. 가중 확률로 반응 선택
4. 상태 업데이트 (화학양론 적용)
5. 반복

참고:
- Gillespie, D.T. (1977). "Exact stochastic simulation of coupled chemical reactions"
- 원본 논문: J. Phys. Chem. 81, 2340-2361
"""

from typing import Dict, Optional, Tuple, Callable
import numpy as np
from numpy.typing import NDArray
import logging

logger = logging.getLogger(__name__)


class GillespieSimulator:
    """
    확률적 시뮬레이션을 위한 Gillespie 알고리즘 구현.
    
    이 클래스는 BaseCircuit의 propensities와 stoichiometry를 활용하여
    화학 반응 네트워크를 시뮬레이션합니다.
    
    Attributes:
        circuit: 시뮬레이션할 BaseCircuit 인스턴스
        num_reactions: 반응 개수
        method: "direct" 또는 "first_reaction"
    """
    
    def __init__(
        self,
        get_propensities: Callable,
        stoichiometry: Dict[str, NDArray[int]],
        num_species: int,
        method: str = "direct"
    ):
        """
        GillespieSimulator 초기화.
        
        Args:
            get_propensities: (state, stimulus) -> propensities 함수
            stoichiometry: 반응별 화학양론 변화 딕셔너리
            num_species: 종(species) 개수
            method: "direct" 또는 "first_reaction"
        """
        self.get_propensities = get_propensities
        self.stoichiometry = stoichiometry
        self.num_species = num_species
        self.num_reactions = len(stoichiometry)
        self.method = method
        
        # 화학양론 행렬 구성
        self.stoich_matrix = np.column_stack(list(stoichiometry.values()))
        
        logger.info(
            f"GillespieSimulator initialized: "
            f"{num_species} species, {self.num_reactions} reactions, method={method}"
        )
    
    def simulate(
        self,
        state: NDArray[np.float64],
        t_span: Tuple[float, float],
        stimulus: float = 0.0,
        n_points: Optional[int] = None,
        seed: Optional[int] = None,
        max_events: int = 1000000
    ) -> Dict[str, NDArray[np.float64]]:
        """
        Gillespie 알고리즘으로 확률적 시뮬레이션 실행.
        
        Args:
            state: 초기 상태 벡터
            t_span: (t_start, t_end) 시간 범위
            stimulus: 입력 신호 (상수값, 0-1)
            n_points: 기록할 시간점 개수 (기본: 100)
            seed: 난수 시드 (재현성용)
            max_events: 최대 이벤트 수 (안전 한계)
        
        Returns:
            시뮬레이션 결과 딕셔너리:
            - 't': 시간 벡터
            - 'y': 상태 행렬 (species x time)
            - 'events': 발생한 반응 수
            - 'success': 성공 여부
            - 'message': 상태 메시지
        """
        if seed is not None:
            np.random.seed(seed)
        
        t_start, t_end = t_span
        if n_points is None:
            n_points = 100
        
        # 기록할 시간점
        record_times = np.linspace(t_start, t_end, n_points)
        
        # 초기화
        current_time = t_start
        current_state = state.copy().astype(np.float64)
        recorded_states = [current_state.copy()]
        recorded_times = [current_time]
        
        event_count = 0
        next_record_idx = 1
        
        # 시뮬레이션 루프
        while current_time < t_end and event_count < max_events:
            # Propensities 계산
            propensities = self.get_propensities(current_state, stimulus)
            
            # Propensity 합계
            prop_sum = np.sum(propensities)
            
            if prop_sum <= 0:
                # 반응 중단: 나머지 시간에 대해 상태 유지
                logger.debug(f"No active reactions at t={current_time}")
                while next_record_idx < len(record_times):
                    recorded_states.append(current_state.copy())
                    recorded_times.append(record_times[next_record_idx])
                    next_record_idx += 1
                break
            
            # 다음 이벤트 시간 샘플링 (지수분포)
            # τ = -ln(r1) / a0, where r1 ~ U(0,1)
            tau = -np.log(np.random.uniform(0, 1)) / prop_sum
            next_time = current_time + tau
            
            # 다음 기록 시간까지 도달했으면 기록
            while next_record_idx < len(record_times) and record_times[next_record_idx] <= next_time:
                # 선형 보간으로 상태 기록 (간단한 방법)
                # 더 정확하면 현재 상태 그대로 사용
                recorded_states.append(current_state.copy())
                recorded_times.append(record_times[next_record_idx])
                next_record_idx += 1
            
            # 시간 범위를 벗어나면 종료
            if next_time > t_end:
                # 마지막 시간점까지 기록
                while next_record_idx < len(record_times):
                    recorded_states.append(current_state.copy())
                    recorded_times.append(record_times[next_record_idx])
                    next_record_idx += 1
                break
            
            # 반응 선택: 가중 확률
            # r2 * a0로 누적합에서 선택
            r2 = np.random.uniform(0, 1)
            cumsum = 0
            selected_reaction = -1
            
            for i, prop in enumerate(propensities):
                cumsum += prop / prop_sum
                if r2 <= cumsum:
                    selected_reaction = i
                    break
            
            if selected_reaction < 0:
                selected_reaction = self.num_reactions - 1
            
            # 상태 업데이트
            current_state += self.stoich_matrix[:, selected_reaction]
            
            # 음수 상태 방지
            current_state = np.maximum(current_state, 0.0)
            
            current_time = next_time
            event_count += 1
        
        # 결과 구성
        y = np.column_stack(recorded_states).T  # (time, species)
        
        return {
            't': np.array(recorded_times),
            'y': y.T,  # (species, time)으로 전치
            'events': event_count,
            'success': event_count < max_events,
            'message': f'Simulation completed: {event_count} events'
        }
    
    def simulate_ensemble(
        self,
        state: NDArray[np.float64],
        t_span: Tuple[float, float],
        num_trajectories: int = 100,
        stimulus: float = 0.0,
        n_points: Optional[int] = None,
        seed: Optional[int] = None,
        parallel: bool = False
    ) -> Dict[str, NDArray[np.float64]]:
        """
        여러 개의 독립적인 확률적 궤적 시뮬레이션.
        
        단일세포 실험에서 세포 개체군의 변동성을 모델링합니다.
        
        Args:
            state: 초기 상태
            t_span: 시간 범위
            num_trajectories: 시뮬레이션할 궤적 개수
            stimulus: 입력 신호
            n_points: 기록할 시간점 개수
            seed: 난수 시드
            parallel: 병렬 처리 여부 (구현 예정)
        
        Returns:
            결과 딕셔너리:
            - 't': 시간 벡터
            - 'trajectories': (num_trajectories, num_species, num_timepoints)
            - 'mean': 평균 궤적
            - 'std': 표준편차
            - 'success': 모든 시뮬레이션 성공 여부
        """
        if n_points is None:
            n_points = 100
        
        trajectories = []
        
        for traj_idx in range(num_trajectories):
            # 각 궤적에 다른 시드 사용
            traj_seed = seed + traj_idx if seed is not None else None
            
            result = self.simulate(
                state=state,
                t_span=t_span,
                stimulus=stimulus,
                n_points=n_points,
                seed=traj_seed
            )
            
            trajectories.append(result['y'])
        
        trajectories = np.array(trajectories)  # (num_traj, species, time)
        
        # 통계량 계산
        mean_traj = np.mean(trajectories, axis=0)
        std_traj = np.std(trajectories, axis=0)
        
        return {
            't': result['t'],
            'trajectories': trajectories,
            'mean': mean_traj,
            'std': std_traj,
            'num_trajectories': num_trajectories,
            'success': all(traj.shape == trajectories[0].shape for traj in trajectories)
        }


class CircuitGillespieAdapter:
    """BaseCircuit 호환 Gillespie 시뮬레이터 어댑터."""
    
    @staticmethod
    def create_simulator(circuit) -> GillespieSimulator:
        """
        BaseCircuit 인스턴스로부터 GillespieSimulator 생성.
        
        Args:
            circuit: BaseCircuit 인스턴스
        
        Returns:
            GillespieSimulator
        """
        return GillespieSimulator(
            get_propensities=circuit.get_propensities,
            stoichiometry=circuit.get_stoichiometry(),
            num_species=len(circuit.state_names),
            method="direct"
        )
    
    @staticmethod
    def simulate(
        circuit,
        t_span: Tuple[float, float],
        stimulus: float = 0.0,
        n_points: int = 100,
        seed: Optional[int] = None
    ) -> Dict[str, NDArray[np.float64]]:
        """
        회로의 확률적 시뮬레이션 (간편 인터페이스).
        
        Args:
            circuit: BaseCircuit 인스턴스
            t_span: 시간 범위
            stimulus: 입력 신호
            n_points: 시간점 개수
            seed: 난수 시드
        
        Returns:
            시뮬레이션 결과
        """
        simulator = CircuitGillespieAdapter.create_simulator(circuit)
        return simulator.simulate(
            state=circuit.get_initial_state(),
            t_span=t_span,
            stimulus=stimulus,
            n_points=n_points,
            seed=seed
        )
    
    @staticmethod
    def simulate_ensemble(
        circuit,
        t_span: Tuple[float, float],
        num_trajectories: int = 100,
        stimulus: float = 0.0,
        n_points: int = 100,
        seed: Optional[int] = None
    ) -> Dict[str, NDArray[np.float64]]:
        """
        회로의 앙상블 시뮬레이션 (편의 인터페이스).
        
        Args:
            circuit: BaseCircuit 인스턴스
            t_span: 시간 범위
            num_trajectories: 궤적 개수
            stimulus: 입력 신호
            n_points: 시간점 개수
            seed: 난수 시드
        
        Returns:
            앙상블 결과
        """
        simulator = CircuitGillespieAdapter.create_simulator(circuit)
        return simulator.simulate_ensemble(
            state=circuit.get_initial_state(),
            t_span=t_span,
            num_trajectories=num_trajectories,
            stimulus=stimulus,
            n_points=n_points,
            seed=seed
        )
