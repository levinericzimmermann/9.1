{ pkgs ? import (fetchTarball "https://github.com/NixOS/nixpkgs/archive/a585b1c70900a1ecf0a782eb0f6f09d405e5e6e3.tar.gz") {} }:

let

  package91 = pkgs.python39Packages.buildPythonPackage rec {
    name = "9.1";
    src = ./9.1;
    propagatedBuildInputs = with pkgs;[ 
        python39Packages.jinja2
    ];
  };

  python91 = pkgs.python39.buildEnv.override {
    extraLibs = [ package91 ];
  };

in

  pkgs.mkShell {
    buildInputs = with pkgs; [
      texlive.combined.scheme-full
      git
      python91
    ];
  }
