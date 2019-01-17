from blueqat import Circuit, BlueqatGlobalSetting
from blueqat.backends.backendbase import Backend
import qulacs

def register_backend(default=False, name="qulacs", allow_overwrite=False):
    """Register Qulacs backend to Blueqat.

    Args:
        default (bool, optional): If true, set as default backend.
        name (str, optional): The name to be registered. (default value is "qulacs".)
        allow_overwrite (bool, optional): If true, allow to overwrite the existing backend.
    """
    BlueqatGlobalSetting.register_backend(name, QulacsBackend, allow_overwrite)
    if default:
        BlueqatGlobalSetting.set_default_backend(name)

class QulacsBackendContext:
    def __init__(self, state, circuit, n_qubits, returns, shots):
        self.state = state
        self.circuit = circuit
        self.n_qubits = n_qubits
        self.returns = returns
        self.shots = shots

class QulacsBackend(Backend):
    def _preprocess_run(self, gates, n_qubits, args, kwargs):
        def parse_args(returns=None, shots=None):
            if returns is None:
                returns = "statevector"
            if returns not in ("statevector", "shots", "_ctx"):
                raise ValueError("`returns` shall be 'statevector' or 'shots'.")
            if shots is None:
                if returns != "shots":
                    shots = 1
                else:
                    shots = 1024
            return returns, shots

        returns, shots = parse_args(*args, **kwargs)
        state = qulacs.QuantumState(n_qubits)
        circuit = qulacs.QuantumCircuit(n_qubits)
        return gates, QulacsBackendContext(state, circuit, n_qubits, returns, shots)

    def _postprocess_run(self, ctx):
        if ctx.returns == "statevector":
            ctx.state.set_zero_state()
            ctx.circuit.update_quantum_state(ctx.state)
            return ctx.state.get_vector()
        if ctx.returns == "shots":
            return "Unimplemented!"
        return ctx

# Single qubit gates
def _get_1q_dispatch(qulacs_meth):
    def _dispatch(self, gate, ctx):
        fn = getattr(ctx.circuit, qulacs_meth)
        for target in gate.target_iter(ctx.n_qubits):
            fn(target, *gate.params)
        return ctx
    return _dispatch

for _gate in "x y z h s t rx ry rz u1 u2 u3".split():
    _blueqat_meth = "gate_" + _gate
    _qulacs_meth = "add_" + _gate.upper() + "_gate"
    setattr(QulacsBackend, _blueqat_meth, _get_1q_dispatch(_qulacs_meth))
setattr(QulacsBackend, "gate_sdg", _get_1q_dispatch("add_Sdag_gate"))
setattr(QulacsBackend, "gate_tdg", _get_1q_dispatch("add_Tdag_gate"))

def _get_2q_dispatch(qulacs_meth):
    def _dispatch(self, gate, ctx):
        fn = getattr(ctx.circuit, qulacs_meth)
        for control, target in gate.control_target_iter(ctx.n_qubits):
            fn(control, target, *gate.params)
        return ctx
    return _dispatch
setattr(QulacsBackend, "gate_cx", _get_2q_dispatch("add_CNOT_gate"))
setattr(QulacsBackend, "gate_cz", _get_2q_dispatch("add_CZ_gate"))
setattr(QulacsBackend, "gate_swap", _get_2q_dispatch("add_SWAP_gate"))
