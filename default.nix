{ pkgs ? import <nixpkgs> { }, }:
let
  inherit (pkgs) stdenv lib;
  py = pkgs.python37;
  pypkgs = pkgs.python37Packages;
  inherit (pypkgs) buildPythonPackage fetchPypi;
  devDeps = with pypkgs; [
    mypy
    black
    pylint
    ptpython
    pytest
    rope
    pydocstyle
    coverage
  ];
  deps = rec {
    fissix = buildPythonPackage rec {
      pname = "fissix";
      version = "19.2b1";
      propagatedBuildInputs = with pypkgs; [ appdirs ];
      src = fetchPypi {
        inherit pname version;
        sha256 = "1ss21icp26l4rv15g1k91349vvaryfcqvidd18ny425bwiwy990c";
      };
      doCheck = false;
    };
    bowler = buildPythonPackage rec {
      pname = "bowler";
      version = "0.8.0";
      propagatedBuildInputs = with pypkgs; [ click sh attrs fissix ];
      src = fetchPypi {
        inherit pname version;
        sha256 = "1clcpznzwp36lmkxsk71h3j8sg25wr5gs1scqfflxn32dlpbmq7k";
      };
      doCheck = false;
    };
  };
in stdenv.mkDerivation rec {
  name = "pyworsener";
  version = "1.0.0";
  src = if lib.inNixShell then null else ./.;
  buildInputs = [ py deps.bowler ] ++ (if lib.inNixShell then devDeps else [ ]);
}
