# Plox
Plox is a simple and lightweight programming language interpreter implemented in Python. This repository contains the source code and documentation for Plox.

## Features
* Syntax: Plox has a C-like syntax that is easy to read and write.
* Interpreter: Plox includes an interpreter that can execute Plox source code.
* Variables: You can define and use variables in Plox to store and manipulate data.
* Control Flow: Plox supports conditional statements (if-else) and loops (while).
* Functions: You can define and call functions in Plox for code reusability.

## Getting Started

1. Clone the repository:

´´´bash
git clone https://github.com/Josemarialanda/plox.git
´´´

2. Change into the project directory:

´´´bash
cd plox
´´´

3. Enter the development environment.

´´´bash
nix develop .
´´´

4. Run the Plox interpreter:

´´´bash
python src/plox.py
´´´

## Install Nix

[NixOS - Getting Nix / NixOS](https://nixos.org/download.html#nix-install-linux)

## Enable flakes

### NixOS

On NixOS set the following options in **configuration.nix** and run `nixos-rebuild`.

```nix
{ pkgs, ... }: {
  nix.settings.experimental-features = [ "nix-command" "flakes" ];
}
```

### Non-NixOS

On non-nixos systems, edit either **~/.config/nix/nix.conf** or **/etc/nix/nix.conf** and add:

```bash
experimental-features = nix-command flakes
```

Here's a handy copy-paste:

```bash
mkdir -p ~/.config/nix
echo "experimental-features = nix-command flakes" >> ~/.config/nix/nix.conf
```


## Acknowledgements
Plox was inspired by the book "Crafting Interpreters" by Bob Nystrom. Special thanks to Bob Nystrom for providing a great resource on language implementation.
