# HeyNoterm

HeyNoterm is a scratch pad for the terminal, designed to help you quickly jot down notes, commands, and ideas while working in the command line.

## What is HeyNoterm?

- A minimalistic, terminal-based scratch pad.
- Organize your thoughts in discrete blocks of text.
- Syntax highlighting for code snippets (Python, Markdown, etc.).
- Math evaluation mode for quick calculations.
- Persistent JSON storage (saved to `~/.heynoterm.json`) so your notes survive restarts.
- Context-aware block operations: add, delete, move, split, and change language on the fly.
- Dark-mode toggle and on-screen help overlay.

## Features

- Add new blocks (`Ctrl+N`), delete blocks (`Ctrl+D`), split blocks (`Ctrl+T`).
- Navigate between blocks (`Ctrl+J` / `Ctrl+K`).
- Change block language (`Ctrl+L`): Python, Markdown, Math.
- Real-time math evaluation in math mode.
- Persistent storage of all blocks in `~/.heynoterm.json`.
<!-- - Toggle dark/light mode (`D`). -->
- On-screen help (`Ctrl+/`) listing all keybindings.

## Installation

We recommend using **uv** to install and manage HeyNoterm, but you can also use **uvx**, **pipx**, or **pip**. Homebrew is not supported.

1. Using uv (recommended)
    ```bash
    uv install heynoterm
    ```

2. Using uvx
    ```bash
    uvx heynoterm
    ```

3. Using pipx
    ```bash
    pipx install heynoterm
    ```

4. Using pip
    ```bash
    pip install heynoterm
    ```

After installation, run HeyNoterm with:
```bash
heynoterm
# or via uv:
uv heynoterm
# or via uvx:
uvx heynoterm
```

## Usage

1. Launch the app: `heynoterm`
2. Type freely to add content in the current block.
3. Use keybindings to manage blocks and switch modes.
4. Press `Ctrl+C` to exit.

All your blocks are automatically saved to `~/.heynoterm.json`.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request on the HeyNoterm GitHub repository.

## License

TBD
