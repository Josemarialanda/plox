{ pkgs ? import <nixpkgs> {}}:

let
  python-packages = p: with p; [
    pygments
  ];
  python-with-packages = pkgs.python311.withPackages python-packages;
  common-utils = with pkgs; [ curl wget gcc ];
in pkgs.mkShell {
  packages = common-utils ++ 
             [ python-with-packages ] ++
             (with pkgs; [ 

             ]);
}