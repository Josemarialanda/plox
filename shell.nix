{ pkgs ? import <nixpkgs> {}}:

let
  python-packages = p: with p; [
    black
    isort
  ];
  python-with-packages = pkgs.python310.withPackages python-packages;
  common-utils = with pkgs; [ curl wget gcc ];
in pkgs.mkShell {
  packages = common-utils ++ 
             [ python-with-packages ] ++
             (with pkgs; [ 

             ]);
  shellHook = ''
    alias format="black src && isort src"
  '';
}