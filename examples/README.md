# TCCDP Examples

This directory contains Jupyter notebook tutorials and examples for the Trainable Cell Circuits Design Platform (TCCDP).

## Available Tutorials

### 1. Transcription Circuit Tutorial (`01_transcription_circuit_tutorial.ipynb`)

A comprehensive introduction to transcription-based learning circuits covering:

- **Introduction** to transcription-based circuits
- **Creating circuits** with custom parameters
- **Running simulations** with different stimuli (constant, step, pulse)
- **Training** with Pavlovian conditioning protocol
- **Visualizing** learning progress and state evolution
- **Computing metrics** for performance evaluation
- **Advanced examples** including:
  - Comparing different learning rules
  - Parameter sensitivity analysis

**Prerequisites**: Basic Python knowledge, understanding of differential equations (helpful but not required)

**Duration**: ~30-45 minutes

## Getting Started

### Installation

Make sure you have TCCDP installed:

```bash
pip install -e .
```

### Running Notebooks

1. Install Jupyter:
```bash
pip install jupyter
```

2. Navigate to the examples directory:
```bash
cd examples
```

3. Start Jupyter:
```bash
jupyter notebook
```

4. Open `01_transcription_circuit_tutorial.ipynb` in your browser

### Using VS Code

If you're using VS Code:

1. Install the Jupyter extension
2. Open the `.ipynb` file
3. Select your Python kernel (the TCCDP virtual environment)
4. Run cells interactively

## Examples by Topic

### Basic Usage
- `01_transcription_circuit_tutorial.ipynb` - Start here!

### Coming Soon
- `02_protein_modification_circuits.ipynb` - Stochastic simulations
- `03_metabolic_circuits.ipynb` - Hybrid simulations
- `04_advanced_training.ipynb` - Custom protocols and learning rules
- `05_multi_circuit_integration.ipynb` - Combining multiple circuits

## Example Data

Some tutorials may generate output data in the `examples/output/` directory. This directory is git-ignored but will be created automatically when needed.

## Troubleshooting

### Common Issues

**Issue**: `ModuleNotFoundError: No module named 'tccdp'`
**Solution**: Make sure you've installed TCCDP with `pip install -e .` from the project root

**Issue**: Plots not showing in Jupyter
**Solution**: Make sure you have `%matplotlib inline` at the top of your notebook

**Issue**: Kernel crashes during training
**Solution**: Try reducing the number of epochs or increasing `dt` in the simulator

### Getting Help

- Check the [main README](../README.md)
- Open an issue on [GitHub](https://github.com/morningpython/trainable_cell_circuits_design/issues)
- Read the [documentation](https://tccdp.readthedocs.io)

## Contributing Examples

We welcome contributions of new examples! Please:

1. Follow the naming convention: `NN_descriptive_name.ipynb`
2. Include a clear introduction and learning objectives
3. Add your example to this README
4. Test that all cells run without errors
5. Submit a pull request

## License

All examples are licensed under the same license as the main project (see [LICENSE](../LICENSE)).
