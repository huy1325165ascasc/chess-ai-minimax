# Chess AI with Minimax and Alpha-Beta Pruning

A Python-based Chess implementation featuring multiple game modes and AI opponents using the Minimax algorithm with Alpha-Beta pruning. The project includes a graphical user interface built with Pygame and supports different gameplay modes with varying levels of AI optimization.

![Chess AI Screenshot](images/screenshot.png)

## Features

- **Multiple Game Modes**:
  - Human vs Human: Play against another person on the same computer
  - Human vs AI: Play against a computer opponent with adjustable difficulty
  - AI vs AI (CPU): Watch two AI opponents battle it out using CPU-optimized algorithms
  - AI vs AI (GPU): Experience faster gameplay with GPU-accelerated AI moves
- **Advanced AI**: Utilizes the Minimax algorithm with Alpha-Beta pruning for smart move selection
- **Performance Optimizations**:
  - CPU-optimized implementation using Numba JIT compilation
  - GPU-accelerated version for faster move calculations
- **Clean GUI**: Simple and intuitive graphical interface built with Pygame
- **Standard Chess Rules**: Implements all standard chess rules and piece movements

## Prerequisites

- Python 3.7 or higher
- pip (Python package installer)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/Chess-minimax.git
   cd Chess-minimax
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Game Modes

### 1. Human vs Human
Play against another person on the same computer.
```bash
python chess-human-vs-human.py
```

### 2. Human vs AI
Play against the computer AI. Choose your color and test your skills!
```bash
python chess_human_vs_ai.py
```

### 3. AI vs AI (CPU)
Watch two AI opponents battle it out using CPU-optimized algorithms.
```bash
python chess_minimax.py
```

### 4. AI vs AI (GPU)
Experience faster gameplay with GPU-accelerated AI moves.
```bash
python chess_gui_withgpu.py
```

### Game Controls (for Human modes)
- **Left-click**: Select and move pieces
- **Right-click**: Deselect a piece
- **ESC**: Exit the game

## Technical Details

### AI Implementation

The AI opponents use the following algorithms and optimizations:
- **Minimax Algorithm**: For decision making
- **Alpha-Beta Pruning**: To optimize the search space
- **Position Evaluation**: Custom evaluation function with piece-square tables
- **Move Ordering**: Sorts moves to improve alpha-beta pruning efficiency

### Performance Optimizations

- **CPU Version**:
  - Numba JIT compilation for CPU acceleration
  - Optimized move generation
  - Efficient board representation using NumPy arrays

- **GPU Version**:
  - CUDA acceleration for parallel move evaluation
  - Optimized for NVIDIA GPUs with CUDA support
  - Significantly faster move calculations for deeper search depths

## Project Structure

```
Chess-minimax/
├── pieces/               # Chess piece images
│   ├── black/           # Black pieces
│   └── white/           # White pieces
├── chess_minimax.py     # AI vs AI (CPU) implementation
├── chess_human_vs_ai.py # Human vs AI game mode
├── chess-human-vs-human.py  # Human vs Human game mode
├── chess_gui_withgpu.py # AI vs AI (GPU-accelerated) implementation
├── chess_gui.py         # Shared GUI components
└── requirements.txt     # Python dependencies
```

## Dependencies

- `pygame`: For the graphical user interface
- `numpy`: For efficient array operations
- `numba`: For JIT compilation and performance optimization
- `asyncio`: For asynchronous operations

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Chess piece images from [public domain sources](https://en.wikipedia.org/wiki/Chess_piece)
- Inspired by various open-source chess implementations

python chess_gui.py
