{ pkgs ? import (fetchTarball "https://github.com/NixOS/nixpkgs/archive/22.05.tar.gz") {} }:

pkgs.mkShell {
  buildInputs = with pkgs; [
    texlive.combined.scheme-full
    git
    python39
    python39Packages.zc-buildout
  ];

  propagatedBuildInputs = with pkgs; [ 
    # Needed for mutwo (primesieve package)
    libstdcxx5 
  ];
}
