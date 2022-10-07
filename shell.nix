# { pkgs ? import (fetchTarball "https://github.com/NixOS/nixpkgs/archive/a585b1c70900a1ecf0a782eb0f6f09d405e5e6e3.tar.gz") {} }:
{ pkgs ? import <nixpkgs> {} }:

let

  mutwo-core-archive = builtins.fetchTarball "https://github.com/mutwo-org/mutwo.core/archive/97aea97f996973955889630c437ceaea405ea0a7.tar.gz";
  mutwo-core = import (mutwo-core-archive + "/default.nix");

  mutwo-pages = pkgs.python39Packages.buildPythonPackage rec {
    name = "mutwo.pages";
    src = ./mutwo.pages;
    propagatedBuildInputs = with pkgs; [
        mutwo-core
        python39Packages.jinja2
    ];
  };

  python91 = pkgs.python39.buildEnv.override {
    extraLibs = with pkgs; [
      python39Packages.ipython
      mutwo-pages
    ];
  };

in

  pkgs.mkShell {
    buildInputs = with pkgs; [
      texlive.combined.scheme-full
      git
      python91
    ];
  }
